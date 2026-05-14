import sqlite3
import os

# Check the database
db_path = "data/ai_security_review.db"

if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Checking database: {db_path}\n")

# Get the schema for submissions table
cursor.execute("PRAGMA table_info(submissions);")
columns = cursor.fetchall()

print("Current columns in submissions table:")
print("-" * 60)
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\n" + "=" * 60)

# Check if our new columns exist
column_names = [col[1] for col in columns]
required_columns = ['uploaded_document_path', 'uploaded_document_name', 'uploaded_document_content']

missing = [col for col in required_columns if col not in column_names]

if missing:
    print(f"\n[MISSING] These columns need to be added: {missing}")
    print("\nAdding columns now...\n")
    
    try:
        for col_name in missing:
            if col_name == 'uploaded_document_path':
                cursor.execute("ALTER TABLE submissions ADD COLUMN uploaded_document_path VARCHAR(500);")
                print(f"[OK] Added {col_name}")
            elif col_name == 'uploaded_document_name':
                cursor.execute("ALTER TABLE submissions ADD COLUMN uploaded_document_name VARCHAR(255);")
                print(f"[OK] Added {col_name}")
            elif col_name == 'uploaded_document_content':
                cursor.execute("ALTER TABLE submissions ADD COLUMN uploaded_document_content TEXT;")
                print(f"[OK] Added {col_name}")
        
        conn.commit()
        print("\n[SUCCESS] All columns added successfully!")
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
else:
    print("\n[OK] All required columns exist!")

conn.close()
