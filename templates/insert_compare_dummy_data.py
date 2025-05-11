import sqlite3
import random

def generate_formatted_text():
    words = [
        "insurance", "policy", "coverage", "premium", "benefit", "claim", "network", "hospital", "cashless", "deductible",
        "sum", "assured", "renewal", "bonus", "waiting", "period", "pre-existing", "disease", "treatment", "room", "rent",
        "ambulance", "tax", "discount", "family", "floater", "critical", "illness", "maternity", "daycare", "AYUSH",
        "wellness", "checkup", "lifetime", "entry", "exit", "age", "no-claim", "bonus", "restoration", "feature", "add-on",
        "rider", "exclusion", "inclusion", "grace", "period", "portability", "settlement", "ratio", "IRDAI", "TPA", "network",
        "hospital", "cashless", "treatment", "policyholder", "beneficiary", "sum insured", "waiting period", "co-payment",
        "sub-limit", "room rent", "pre-authorization", "claim settlement", "network hospital", "cashless facility", "renewal",
        "lifetime", "entry age", "exit age", "no-claim bonus", "restoration benefit", "add-on cover", "critical illness",
        "maternity cover", "daycare procedure", "AYUSH treatment", "wellness program", "health checkup", "tax benefit"
    ]
    random.shuffle(words)
    text = ""
    for i in range(0, 200, 40):
        para = " ".join(words[i:i+40])
        if i == 0:
            para = f"<p><b style='color:#d50060'>{para}</b></p>"
        elif i == 40:
            para = f"<p style='color:#1976d2'>{para}</p>"
        else:
            para = f"<p>{para}</p>"
        text += para
    return text

def main():
    # Connect to your insurance.db
    conn = sqlite3.connect('insurance.db')
    cur = conn.cursor()

    # Adjust table/column names as per your schema
    # Example assumes a table named 'policies' with columns: id, name, vendor
    cur.execute("SELECT id, name, vendor FROM policies")
    policies = cur.fetchall()

    # Create the policy_comparisons table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS policy_comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy1_id INTEGER NOT NULL,
            policy2_id INTEGER NOT NULL,
            compare_text TEXT,
            UNIQUE(policy1_id, policy2_id)
        )
    """)

    # Insert comparison text for a few policy pairs (first 3 unique pairs)
    for i in range(min(3, len(policies))):
        for j in range(i+1, min(3, len(policies))):
            policy1_id, policy1_name, vendor1 = policies[i]
            policy2_id, policy2_name, vendor2 = policies[j]
            compare_text = generate_formatted_text()
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO policy_comparisons (policy1_id, policy2_id, compare_text) VALUES (?, ?, ?)",
                    (policy1_id, policy2_id, compare_text)
                )
            except Exception as e:
                print(f"Error inserting comparison for {policy1_name} vs {policy2_name}: {e}")

    conn.commit()
    print("Sample comparisons with formatted text inserted into insurance.db.")
    conn.close()

if __name__ == "__main__":
    main()