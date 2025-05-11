import openai
import configparser
import sqlite3
import time

# Load config
config = configparser.ConfigParser()
config.read('/home/ravi/ins/config.ini')
openai.api_key = config['openai']['api_key']
model = config['openai']['model']

# Connect to DB
conn = sqlite3.connect("/home/ravi/ins/insurance.db")
conn.row_factory = sqlite3.Row
policies = conn.execute("SELECT id, details FROM policy").fetchall()

for i in range(len(policies)):
    for j in range(i+1, len(policies)):
        id1, details1 = policies[i]['id'], policies[i]['details']
        id2, details2 = policies[j]['id'], policies[j]['details']
        # Check if already exists
        exists = conn.execute(
            "SELECT 1 FROM compare_reports WHERE policy1_id=? AND policy2_id=?",
            (id1, id2)
        ).fetchone()
        if exists:
            continue
        prompt = (
            "Compare the following two policy details and generate a concise, clear comparison report:\n"
            f"Policy 1: {details1}\n"
            f"Policy 2: {details2}\n"
            "Highlight similarities and differences in features, benefits, and limitations."
        )
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            report = response.choices[0].message.content.strip()
            conn.execute(
                "INSERT INTO compare_reports (policy1_id, policy2_id, report) VALUES (?, ?, ?)",
                (id1, id2, report)
            )
            conn.commit()
            print(f"Generated report for {id1} vs {id2}")
            time.sleep(1)  # Be nice to the API
        except Exception as e:
            print(f"Error for {id1} vs {id2}: {e}")
            time.sleep(5)
conn.close()