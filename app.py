from flask import Flask, render_template, request, jsonify
import sqlite3
import json
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import SelectField
import os
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
csrf = CSRFProtect(app)

logging.basicConfig(level=logging.INFO)

class PolicyForm(FlaskForm):
    insurer = SelectField('Insurer', coerce=int)
    policy = SelectField('Policy', coerce=int)

def get_db_connection():
    conn = sqlite3.connect("insurance.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_score_color(tag):
    if "Good" in tag or tag.strip().lower() == "yes":
        return "green"
    elif "Decent" in tag:
        return "orange"
    else:
        return "red"

def get_popular_comparisons():
    conn = get_db_connection()
    policies = conn.execute("SELECT p.id, p.name, p.overall_score, i.name as insurer FROM policy p JOIN insurer i ON p.insurer_id = i.id ORDER BY RANDOM() LIMIT 8").fetchall()
    conn.close()
    pairs = []
    for i in range(0, min(8, len(policies)), 2):
        if i+1 < len(policies):
            pairs.append((policies[i], policies[i+1]))
    return pairs

@app.route("/")
def home():
    conn = get_db_connection()
    plans = conn.execute(
        "SELECT p.name, p.overall_score, p.insurer_rating, p.feature_rating, p.affordability_rating, i.name as insurer "
        "FROM policy p JOIN insurer i ON p.insurer_id = i.id "
        "ORDER BY p.overall_score DESC LIMIT 5"
    ).fetchall()
    conn.close()
    top_plans = [dict(plan) for plan in plans]
    return render_template("index.html", top_plans=top_plans)

@app.route("/scorecard", methods=["GET", "POST"])
def scorecard():
    conn = get_db_connection()
    insurers = conn.execute("SELECT * FROM insurer").fetchall()
    form = PolicyForm()
    form.insurer.choices = [(i['id'], i['name']) for i in insurers]

    selected_insurer_id = form.insurer.data or request.form.get('insurer') or insurers[0]['id']
    policies = conn.execute("SELECT * FROM policy WHERE insurer_id=?", (selected_insurer_id,)).fetchall()
    form.policy.choices = [(p['id'], p['name']) for p in policies]

    selected_policy_id = form.policy.data or request.form.get('policy') or (policies[0]['id'] if policies else None)
    if selected_policy_id and not any(p['id'] == int(selected_policy_id) for p in policies):
        selected_policy_id = policies[0]['id'] if policies else None

    policy_row = conn.execute("SELECT * FROM policy WHERE id=?", (selected_policy_id,)).fetchone() if selected_policy_id else None
    features = conn.execute("SELECT * FROM feature WHERE policy_id=?", (selected_policy_id,)).fetchall() if selected_policy_id else []
    scores = None
    if policy_row:
        scores = {
            'overall_score': policy_row['overall_score'],
            'insurer_rating': policy_row['insurer_rating'],
            'feature_rating': policy_row['feature_rating'],
            'affordability_rating': policy_row['affordability_rating']
        }
    conn.close()

    policy_data = {
        "InsurerDetails": json.loads(policy_row["details"]) if policy_row else {},
        "PolicyFeatures": [dict(f) for f in features]
    }
    for f in policy_data["PolicyFeatures"]:
        f["FeatureName"] = f["name"]
        f["FeatureOffered"] = f["offered"]
        f["Explanation"] = f["explanation"]
        f["Details"] = f["details"]
        f["Caveats"] = f["caveats"]

    mandatory_features = [f for f in policy_data["PolicyFeatures"] if f.get("category", "Good To Have") == "Mandatory"]
    good_features = [f for f in policy_data["PolicyFeatures"] if f.get("category", "Good To Have") != "Mandatory"]

    return render_template(
        "scorecard.html",
        insurers=insurers,
        policies=policies,
        selected_insurer_id=selected_insurer_id,
        selected_policy_id=selected_policy_id,
        policy_data=policy_data,
        get_score_color=get_score_color,
        mandatory_features=mandatory_features,
        good_features=good_features,
        scores=scores,
        form=form
    )

@app.route("/compare", methods=["GET", "POST"])
def compare():
    import sys
    print("[DEBUG] compare route called", file=sys.stderr)
    conn = get_db_connection()
    insurers = conn.execute("SELECT * FROM insurer").fetchall()
    policy1 = policy2 = features1 = features2 = None
    all_features = []
    error = None
    if request.method == "POST":
        print("[DEBUG] POST data:", dict(request.form), file=sys.stderr)
        policy1_id = request.form.get("policy1")
        policy2_id = request.form.get("policy2")
        insurer1_id = request.form.get("insurer1")
        insurer2_id = request.form.get("insurer2")
        print(f"[DEBUG] policy1_id={policy1_id}, policy2_id={policy2_id}, insurer1_id={insurer1_id}, insurer2_id={insurer2_id}", file=sys.stderr)
        # Validate both policies are selected
        if not policy1_id or not policy2_id:
            error = "Please select both policies to compare."
            print(f"[DEBUG] Error: {error}", file=sys.stderr)
        else:
            # Validate that selected policies belong to selected insurers
            valid1 = conn.execute("SELECT 1 FROM policy WHERE id=? AND insurer_id=?", (policy1_id, insurer1_id)).fetchone()
            valid2 = conn.execute("SELECT 1 FROM policy WHERE id=? AND insurer_id=?", (policy2_id, insurer2_id)).fetchone()
            print(f"[DEBUG] valid1={valid1}, valid2={valid2}", file=sys.stderr)
            if not valid1 or not valid2:
                error = "Selected policy does not belong to the selected insurer."
                print(f"[DEBUG] Error: {error}", file=sys.stderr)
            else:
                policy1 = conn.execute("SELECT p.*, i.name as insurer FROM policy p JOIN insurer i ON p.insurer_id = i.id WHERE p.id=?", (policy1_id,)).fetchone()
                policy2 = conn.execute("SELECT p.*, i.name as insurer FROM policy p JOIN insurer i ON p.insurer_id = i.id WHERE p.id=?", (policy2_id,)).fetchone()
                print(f"[DEBUG] policy1={dict(policy1) if policy1 else None}", file=sys.stderr)
                print(f"[DEBUG] policy2={dict(policy2) if policy2 else None}", file=sys.stderr)
                f1 = conn.execute("SELECT * FROM feature WHERE policy_id=?", (policy1_id,)).fetchall()
                f2 = conn.execute("SELECT * FROM feature WHERE policy_id=?", (policy2_id,)).fetchall()
                features1 = {f["name"]: f["offered"] for f in f1}
                features2 = {f["name"]: f["offered"] for f in f2}
                all_features = sorted(set(features1) | set(features2))
                print(f"[DEBUG] features1 keys: {list(features1.keys())}", file=sys.stderr)
                print(f"[DEBUG] features2 keys: {list(features2.keys())}", file=sys.stderr)
    conn.close()
    popular_comparisons = get_popular_comparisons()
    print(f"[DEBUG] Rendering compare.html with error={error}", file=sys.stderr)
    return render_template(
        "compare.html",
        insurers=insurers,
        popular_comparisons=popular_comparisons,
        policy1=policy1,
        policy2=policy2,
        features1=features1,
        features2=features2,
        all_features=all_features,
        error=error,
        get_score_color=get_score_color
    )

@app.route("/api/policies/<int:insurer_id>")
def api_policies(insurer_id):
    conn = get_db_connection()
    policies = conn.execute("SELECT id, name FROM policy WHERE insurer_id=?", (insurer_id,)).fetchall()
    conn.close()
    return jsonify([{"id": p["id"], "name": p["name"]} for p in policies])

@app.route("/api/policy/<int:policy_id>")
def api_policy(policy_id):
    conn = get_db_connection()
    policy_row = conn.execute("SELECT * FROM policy WHERE id=?", (policy_id,)).fetchone()
    features = conn.execute("SELECT * FROM feature WHERE policy_id=?", (policy_id,)).fetchall()
    conn.close()
    policy_data = {
        "InsurerDetails": json.loads(policy_row["details"]),
        "PolicyFeatures": [dict(f) for f in features]
    }
    return jsonify(policy_data)

if __name__ == "__main__":
    app.run(debug=True)