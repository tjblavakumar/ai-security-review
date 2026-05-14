import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "data" / "ai_security_review.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("RISK RULES IN DATABASE:")
print("=" * 60)
cursor.execute("SELECT id, name, description, risk_value, is_active FROM risk_rules")
rules = cursor.fetchall()

if not rules:
    print("No rules found in database!")
else:
    for row in rules:
        print(f"\nID: {row[0]}")
        print(f"  Name: {row[1]}")
        print(f"  Description: {row[2]}")
        print(f"  Risk Value: {row[3]}")
        print(f"  Active: {row[4]}")

print("\n" + "=" * 60)
print("RISK THRESHOLDS IN DATABASE:")
print("=" * 60)
cursor.execute("SELECT id, level, min_score, max_score, color FROM risk_thresholds")
thresholds = cursor.fetchall()

if not thresholds:
    print("No thresholds found in database!")
else:
    for row in thresholds:
        print(f"\nID: {row[0]}")
        print(f"  Level: {row[1]}")
        print(f"  Range: {row[2]} - {row[3]}")
        print(f"  Color: {row[4]}")

conn.close()
