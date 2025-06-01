from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
import sqlite3
import json
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import SelectField, StringField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed
import os
import logging
import bleach
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
csrf = CSRFProtect(app)

# Add rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

logging.basicConfig(level=logging.INFO)

class PolicyForm(FlaskForm):
    insurer = SelectField('Insurer', coerce=int)
    policy = SelectField('Policy', coerce=int)

class CompareForm(FlaskForm):
    insurer1 = SelectField('Insurer 1', coerce=int)
    policy1 = SelectField('Policy 1', coerce=int)
    insurer2 = SelectField('Insurer 2', coerce=int)
    policy2 = SelectField('Policy 2', coerce=int)

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    author = StringField('Author', validators=[Length(max=100)])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])

class PersonalizeForm(FlaskForm):
    category = SelectField('Category', choices=[])

BLOG_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'blog_images')
os.makedirs(BLOG_UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = BLOG_UPLOAD_FOLDER

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
    policies = conn.execute(
        "SELECT p.id, p.name, p.overall_score, i.name as insurer, i.id as insurer_id FROM policy p JOIN insurer i ON p.insurer_id = i.id ORDER BY RANDOM() LIMIT 8"
    ).fetchall()
    conn.close()
    pairs = []
    for i in range(0, min(8, len(policies)), 2):
        if i+1 < len(policies):
            pairs.append((policies[i], policies[i+1]))
    return pairs

@app.route("/")
def home():
    lang = request.args.get('lang', 'en')
    translations = {}
    if lang == 'hi':
        try:
            with open(os.path.join(app.root_path, 'static', 'translations_hi.json'), encoding='utf-8') as f:
                translations = json.load(f)
        except Exception as e:
            print(f"[DEBUG] Could not load Hindi translations: {e}")
    elif lang == 'kn':
        try:
            with open(os.path.join(app.root_path, 'static', 'translations_kn.json'), encoding='utf-8') as f:
                translations = json.load(f)
        except Exception as e:
            print(f"[DEBUG] Could not load Kannada translations: {e}")
    with get_db_connection() as conn:
        plans = conn.execute(
            "SELECT p.name, p.overall_score, p.insurer_rating, p.feature_rating, p.affordability_rating, i.name as insurer "
            "FROM policy p JOIN insurer i ON p.insurer_id = i.id "
            "ORDER BY p.overall_score DESC LIMIT 5"
        ).fetchall()
        top_plans = [dict(plan) for plan in plans]
    return render_template("index.html", top_plans=top_plans, translations=translations, lang=lang)

@app.route("/scorecard", methods=["GET", "POST"])
def scorecard():
    with get_db_connection() as conn:
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

        policy_data = {
            "InsurerDetails": json.loads(policy_row["details"]) if policy_row and policy_row["details"] else {},
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

    form.insurer.data = int(selected_insurer_id) if selected_insurer_id else None
    form.policy.data = int(selected_policy_id) if selected_policy_id else None
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
    logging.info("[DEBUG] compare route called")
    form = CompareForm()
    policy1_details = {}
    policy2_details = {}
    with get_db_connection() as conn:
        insurers = conn.execute("SELECT * FROM insurer").fetchall()
        insurer_choices = [(i['id'], i['name']) for i in insurers]
        form.insurer1.choices = insurer_choices
        form.insurer2.choices = insurer_choices
        # Set default insurer if not set
        selected_insurer1 = form.insurer1.data or request.form.get('insurer1') or (insurers[0]['id'] if insurers else None)
        selected_insurer2 = form.insurer2.data or request.form.get('insurer2') or (insurers[1]['id'] if len(insurers) > 1 else (insurers[0]['id'] if insurers else None))
        policies1 = conn.execute("SELECT id, name FROM policy WHERE insurer_id=?", (selected_insurer1,)).fetchall() if selected_insurer1 else []
        policies2 = conn.execute("SELECT id, name FROM policy WHERE insurer_id=?", (selected_insurer2,)).fetchall() if selected_insurer2 else []
        form.policy1.choices = [(p['id'], p['name']) for p in policies1]
        form.policy2.choices = [(p['id'], p['name']) for p in policies2]
        # Robustly determine selected policy for each dropdown
        selected_policy1 = (form.policy1.data or request.form.get('policy1'))
        if not selected_policy1 and policies1:
            selected_policy1 = str(policies1[0]['id'])
        selected_policy2 = (form.policy2.data or request.form.get('policy2'))
        if not selected_policy2 and policies2:
            selected_policy2 = str(policies2[0]['id'])
        policy1 = policy2 = features1 = features2 = None
        features1_full = features2_full = None
        all_features = []
        error = None
        compare_summary = None
        if form.validate_on_submit():
            policy1_id = form.policy1.data
            policy2_id = form.policy2.data
            insurer1_id = form.insurer1.data
            insurer2_id = form.insurer2.data
            # Validate that selected policies belong to selected insurers
            valid1 = conn.execute("SELECT 1 FROM policy WHERE id=? AND insurer_id=?", (policy1_id, insurer1_id)).fetchone()
            valid2 = conn.execute("SELECT 1 FROM policy WHERE id=? AND insurer_id=?", (policy2_id, insurer2_id)).fetchone()
            if not valid1 or not valid2:
                error = "Selected policy does not belong to the selected insurer."
            else:
                policy1 = conn.execute("SELECT p.*, i.name as insurer FROM policy p JOIN insurer i ON p.insurer_id = i.id WHERE p.id=?", (policy1_id,)).fetchone()
                policy2 = conn.execute("SELECT p.*, i.name as insurer FROM policy p JOIN insurer i ON p.insurer_id = i.id WHERE p.id=?", (policy2_id,)).fetchone()
                # Parse details JSON for each policy
                policy1_details = json.loads(policy1['details']) if policy1 and policy1['details'] else {}
                policy2_details = json.loads(policy2['details']) if policy2 and policy2['details'] else {}
                f1 = conn.execute("SELECT * FROM feature WHERE policy_id=?", (policy1_id,)).fetchall()
                f2 = conn.execute("SELECT * FROM feature WHERE policy_id=?", (policy2_id,)).fetchall()
                features1 = {f["name"]: f["offered"] for f in f1}
                features2 = {f["name"]: f["offered"] for f in f2}
                features1_full = {f["name"]: f for f in f1}
                features2_full = {f["name"]: f for f in f2}
                all_features = sorted(set(features1) | set(features2))
                # Fetch feature-level compare reports
                compare_reports_rows = conn.execute("""
                    SELECT feature_name, report FROM feature_compare_reports
                    WHERE (policy1_id=? AND policy2_id=?) OR (policy1_id=? AND policy2_id=?)
                """, (policy1_id, policy2_id, policy2_id, policy1_id)).fetchall()
                feature_compare_reports = {row['feature_name']: row['report'] for row in compare_reports_rows}
                row = conn.execute("SELECT report FROM compare_reports WHERE policy1_id=? AND policy2_id=?", (policy1_id, policy2_id)).fetchone()
                if not row:
                    row = conn.execute("SELECT report FROM compare_reports WHERE policy1_id=? AND policy2_id=?", (policy2_id, policy1_id)).fetchone()
                if row:
                    allowed_tags = [
                        'p', 'b', 'i', 'strong', 'em', 'ul', 'ol', 'li', 'br', 'span', 'u', 'a'
                    ]
                    allowed_attrs = {
                        'span': ['style'],
                        'a': ['href', 'title', 'target', 'rel'],
                        'p': ['style'],
                        'b': ['style'],
                    }
                    compare_summary = bleach.clean(row[0], tags=allowed_tags, attributes=allowed_attrs, strip=True)
        popular_comparisons = get_popular_comparisons()
        return render_template(
            "compare.html",
            insurers=insurers,
            popular_comparisons=popular_comparisons,
            policy1=policy1,
            policy2=policy2,
            features1=features1,
            features2=features2,
            features1_full=features1_full,
            features2_full=features2_full,
            all_features=all_features,
            error=error,
            get_score_color=get_score_color,
            compare_summary=compare_summary,
            form=form,
            selected_policy1=selected_policy1,
            selected_policy2=selected_policy2,
            policy1_details=policy1_details,
            policy2_details=policy2_details,
            feature_compare_reports=feature_compare_reports if 'feature_compare_reports' in locals() else {}
        )

@app.route("/personalize", methods=["GET", "POST"])
def personalize():
    categories = [
        ("Family", "Family"),
        ("Senior Citizen", "Senior Citizen"),
        ("Critical Illness", "Critical Illness"),
        ("Maternity", "Maternity"),
        ("Budget", "Budget")
    ]
    form = PersonalizeForm()
    form.category.choices = categories
    selected_category = form.category.data or request.form.get('category') or 'Family'
    with get_db_connection() as conn:
        rows = conn.execute('''
            SELECT c.category, p.name as policy_name, i.name as insurer, p.overall_score, p.insurer_rating, p.feature_rating, p.affordability_rating
            FROM custom_category_top_policies c
            JOIN policy p ON c.policy_id = p.id
            JOIN insurer i ON c.insurer_id = i.id
            WHERE c.category = ?
            ORDER BY c.score DESC, p.overall_score DESC
            LIMIT 5
        ''', (selected_category,)).fetchall()
        top_plans = [dict(row) for row in rows]
    return render_template("personalize.html", categories=categories, selected_category=selected_category, top_plans=top_plans, form=form)

@app.route("/api/policies/<int:insurer_id>")
@limiter.limit("30/minute")
def api_policies(insurer_id):
    with get_db_connection() as conn:
        policies = conn.execute("SELECT id, name FROM policy WHERE insurer_id=?", (insurer_id,)).fetchall()
        return jsonify([{"id": p["id"], "name": p["name"]} for p in policies])

@app.route("/api/policy/<int:policy_id>")
@limiter.limit("30/minute")
def api_policy(policy_id):
    with get_db_connection() as conn:
        policy_row = conn.execute("SELECT * FROM policy WHERE id=?", (policy_id,)).fetchone()
        features = conn.execute("SELECT * FROM feature WHERE policy_id=?", (policy_id,)).fetchall()
        policy_data = {
            "InsurerDetails": json.loads(policy_row["details"]),
            "PolicyFeatures": [dict(f) for f in features]
        }
        return jsonify(policy_data)

@app.route("/api/scorecard_by_name")
def api_scorecard_by_name():
    insurer = request.args.get('insurer')
    policy = request.args.get('policy')
    if not insurer or not policy:
        return jsonify({'error': 'Missing insurer or policy'}), 400
    with get_db_connection() as conn:
        policy_row = conn.execute("SELECT * FROM policy WHERE name=? AND insurer_id=(SELECT id FROM insurer WHERE name=?)", (policy, insurer)).fetchone()
        if not policy_row:
            return jsonify({'error': 'Policy not found'}), 404
        features = conn.execute("SELECT * FROM feature WHERE policy_id=?", (policy_row['id'],)).fetchall()
        scores = {
            'overall_score': policy_row['overall_score'],
            'insurer_rating': policy_row['insurer_rating'],
            'feature_rating': policy_row['feature_rating'],
            'affordability_rating': policy_row['affordability_rating']
        }
        policy_data = {
            "InsurerDetails": json.loads(policy_row["details"]) if policy_row and policy_row["details"] else {},
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
        return jsonify({
            'policy_data': policy_data,
            'scores': scores,
            'mandatory_features': mandatory_features,
            'good_features': good_features
        })

@app.route('/blog')
def blog_list():
    conn = get_db_connection()
    blogs = conn.execute('SELECT * FROM blog ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('blog_list.html', blogs=blogs)

@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    conn = get_db_connection()
    blog = conn.execute('SELECT * FROM blog WHERE id=?', (blog_id,)).fetchone()
    conn.close()
    if not blog:
        return "Blog not found", 404
    return render_template('blog_detail.html', blog=blog)

@app.route('/blog/new', methods=['GET', 'POST'])
def blog_new():
    form = BlogForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO blog (title, content, author, image) VALUES (?, ?, ?, ?)',
            (form.title.data, form.content.data, form.author.data, image_filename)
        )
        conn.commit()
        conn.close()
        flash('Blog post created!', 'success')
        return redirect(url_for('blog_list'))
    return render_template('blog_form.html', form=form, action='New')

@app.route('/blog/<int:blog_id>/edit', methods=['GET', 'POST'])
def blog_edit(blog_id):
    conn = get_db_connection()
    blog = conn.execute('SELECT * FROM blog WHERE id=?', (blog_id,)).fetchone()
    if not blog:
        conn.close()
        return "Blog not found", 404
    form = BlogForm(data=blog)
    if form.validate_on_submit():
        image_filename = blog['image']
        if form.image.data:
            image_file = form.image.data
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        conn.execute(
            'UPDATE blog SET title=?, content=?, author=?, image=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
            (form.title.data, form.content.data, form.author.data, image_filename, blog_id)
        )
        conn.commit()
        conn.close()
        flash('Blog post updated!', 'success')
        return redirect(url_for('blog_detail', blog_id=blog_id))
    conn.close()
    return render_template('blog_form.html', form=form, action='Edit', blog=blog)

@app.route('/static/blog_images/<filename>')
def blog_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)