import sqlite3
import json

# Load JSON data
with open("src/data.json", "r") as file:
    data = json.load(file)

conn = sqlite3.connect("insurance.db")
c = conn.cursor()

# Create tables
c.execute("""
CREATE TABLE IF NOT EXISTS insurer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS policy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insurer_id INTEGER,
    name TEXT,
    details TEXT,
    overall_score INTEGER,
    insurer_rating INTEGER,
    feature_rating INTEGER,
    affordability_rating INTEGER,
    FOREIGN KEY(insurer_id) REFERENCES insurer(id)
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS feature (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER,
    name TEXT,
    offered TEXT,
    explanation TEXT,
    details TEXT,
    caveats TEXT,
    category TEXT,
    why_matters TEXT,
    FOREIGN KEY(policy_id) REFERENCES policy(id)
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS addon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_id INTEGER,
    name TEXT,
    description TEXT,
    details TEXT,
    FOREIGN KEY(policy_id) REFERENCES policy(id)
);
""")

c.execute("CREATE INDEX IF NOT EXISTS idx_policy_insurer_id ON policy(insurer_id)")
c.execute("CREATE INDEX IF NOT EXISTS idx_feature_policy_id ON feature(policy_id)")

def insert_insurer(name):
    c.execute("INSERT OR IGNORE INTO insurer (name) VALUES (?)", (name,))
    c.execute("SELECT id FROM insurer WHERE name=?", (name,))
    return c.fetchone()[0]

def insert_policy(insurer_id, name, details):
    import random
    overall_score = random.randint(1, 10)
    insurer_rating = random.randint(1, 10)
    feature_rating = random.randint(1, 10)
    affordability_rating = random.randint(1, 10)
    c.execute("""
        INSERT INTO policy (insurer_id, name, details, overall_score, insurer_rating, feature_rating, affordability_rating)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (insurer_id, name, json.dumps(details), overall_score, insurer_rating, feature_rating, affordability_rating))
    return c.lastrowid

def insert_feature(policy_id, feature):
    c.execute("""
        INSERT INTO feature (policy_id, name, offered, explanation, details, caveats, category, why_matters)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        policy_id,
        feature["FeatureName"],
        feature["FeatureOffered"],
        feature["Explanation"],
        feature["Details"],
        feature["Caveats"],
        feature.get("Category", "Good To Have"),
        feature.get("WhyMatters", "")
    ))

# Insert HDFC Ergo / Optima Secure
insurer_id = insert_insurer(data["InsurerDetails"]["Insurer"])
policy_id = insert_policy(insurer_id, data["InsurerDetails"]["InsurancePolicy"], data["InsurerDetails"])
for feature in data["PolicyFeatures"]:
    insert_feature(policy_id, feature)

# Insert HDFC ERGO 1 / Optima Secure1 (replica)
insurer_id2 = insert_insurer("HDFC ERGO 1")
policy_details2 = dict(data["InsurerDetails"])
policy_details2["InsurancePolicy"] = "Optima Secure1"
policy_details2["Insurer"] = "HDFC ERGO 1"  # Ensure insurer name is correct
policy_id2 = insert_policy(insurer_id2, "Optima Secure1", policy_details2)
for feature in data["PolicyFeatures"]:
    feature2 = dict(feature)
    feature2["InsurancePolicy"] = "Optima Secure1"
    insert_feature(policy_id2, feature2)

# Insert two more policies for each insurer for testing
for insurer_id, insurer_name in [
    (insurer_id, data["InsurerDetails"]["Insurer"]),
    (insurer_id2, "HDFC ERGO 1")
]:
    for suffix in ["Plus", "Elite"]:
        policy_details = dict(data["InsurerDetails"])
        policy_details["InsurancePolicy"] = f"{policy_details['InsurancePolicy']} {suffix}"
        policy_details["Insurer"] = insurer_name
        policy_id_extra = insert_policy(insurer_id, policy_details["InsurancePolicy"], policy_details)
        for feature in data["PolicyFeatures"]:
            feature_extra = dict(feature)
            feature_extra["InsurancePolicy"] = policy_details["InsurancePolicy"]
            # Optionally randomize FeatureOffered for more variety
            import random
            if random.random() < 0.3:
                feature_extra["FeatureOffered"] = random.choice(["Yes", "No"])
            insert_feature(policy_id_extra, feature_extra)

# c.execute("ALTER TABLE feature ADD COLUMN why_matters TEXT")  # Already exists, do not run again

why_matters_map = {
    "No Co-Pay": ("You pay nothing extra during hospitalization.", "No out-of-pocket costs during claims."),
    "No Room Rent Restriction": ("Any hospital room can be chosen without extra cost.", "Choose any hospital room freely."),
    "No Disease Wise Sub-limits": ("Full sum insured is available for any illness.", "Full cover for any illness."),
    "Low PED Waiting Period": ("Pre-existing diseases are covered after a short wait.", "Pre-existing conditions covered sooner."),
    "Pre and Post-Hospitalization Care": ("Expenses before and after hospital stay are covered.", "Covers costs before and after admission."),
    "Coverage for Daycare Treatments": ("Short procedures are fully covered.", "Daycare treatments are included."),
    "Restoration Benefit": ("Sum insured is refilled after a claim.", "More coverage after a claim."),
    "Bonus for No Claim": ("Coverage increases each claim-free year.", "Rewards you for staying healthy."),
    "Free Health Checkups": ("Annual health checkups are included.", "Encourages regular health monitoring."),
    "Cover for Consumables": ("Medical supplies during treatment are covered.", "Pays for medical supplies."),
    "Domiciliary Coverage": ("Home treatment is covered if hospitalization isn’t possible.", "Covers treatment at home."),
    "Cover for Alternative Treatments": ("Ayurveda, Homeopathy, and more are covered.", "Pays for alternative treatments."),
    "Maternity Benefits": ("Childbirth and related expenses are covered.", "Covers maternity expenses.")
}

for feature_name, (details, why_matters) in why_matters_map.items():
    c.execute("UPDATE feature SET why_matters=? WHERE name=?", (why_matters, feature_name))

conn.commit()
conn.close()
print("Database initialized.")