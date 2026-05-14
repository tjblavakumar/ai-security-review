"""
Quick migration script to add document upload columns to submissions table.
Run this from the backend directory: python run_migration.py
"""

import sqlite3
import os

# Path to the database
db_path = "data/ai_security_review.db"

if not os.path.exists(db_path):
    print(f"Error: Database file '{db_path}' not found!")
    print("Make sure you're running this from the backend directory.")
    exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Running migration to add document upload columns...")

try:
    # Add the three new columns
    cursor.execute("ALTER TABLE submissions ADD COLUMN uploaded_document_path VARCHAR(500);")
    print("[OK] Added uploaded_document_path column")
    
    cursor.execute("ALTER TABLE submissions ADD COLUMN uploaded_document_name VARCHAR(255);")
    print("[OK] Added uploaded_document_name column")
    
    cursor.execute("ALTER TABLE submissions ADD COLUMN uploaded_document_content TEXT;")
    print("[OK] Added uploaded_document_content column")
    
    # Commit the changes
    conn.commit()
    print("\n[SUCCESS] Migration completed successfully!")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print(f"\n[WARNING] Columns already exist: {e}")
        print("Migration may have already been run.")
    else:
        print(f"\n[ERROR] Error: {e}")
        conn.rollback()
        exit(1)
        
finally:
    conn.close()

print("\nYou can now restart the backend server.")
