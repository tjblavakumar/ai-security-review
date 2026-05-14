"""
Migration script to add risk scoring tables and columns
Run this to update your existing database with risk scoring features
"""

import sqlite3
from pathlib import Path

def migrate_database():
    """Add risk scoring columns and tables to existing database"""
    
    # Try common database locations
    possible_paths = [
        Path(__file__).parent / "data" / "ai_security_review.db",
        Path(__file__).parent / "security_review.db",
        Path(__file__).parent / "data" / "security_review.db",
    ]
    
    db_path = None
    for path in possible_paths:
        if path.exists():
            db_path = path
            break
    
    if not db_path:
        print("Database not found in common locations:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\nDatabase will be created when you start the backend server.")
        return
    
    print(f"Migrating database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Add risk_weight column to questions table if it doesn't exist
        print("Adding risk_weight column to questions table...")
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN risk_weight INTEGER DEFAULT 5")
            print("[OK] Added risk_weight column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("[OK] risk_weight column already exists")
            else:
                raise
        
        # 2. Add risk_score and risk_level columns to submissions table if they don't exist
        print("Adding risk_score column to submissions table...")
        try:
            cursor.execute("ALTER TABLE submissions ADD COLUMN risk_score REAL")
            print("[OK] Added risk_score column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("[OK] risk_score column already exists")
            else:
                raise
        
        print("Adding risk_level column to submissions table...")
        try:
            cursor.execute("ALTER TABLE submissions ADD COLUMN risk_level VARCHAR(20)")
            print("[OK] Added risk_level column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("[OK] risk_level column already exists")
            else:
                raise
        
        # 3. Create risk_rules table
        print("Creating risk_rules table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                keywords TEXT NOT NULL,
                high_risk_answers TEXT NOT NULL,
                risk_value INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Created risk_rules table")
        
        # 4. Create risk_thresholds table
        print("Creating risk_thresholds table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_thresholds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level VARCHAR(20) NOT NULL UNIQUE,
                min_score REAL NOT NULL,
                max_score REAL NOT NULL,
                color VARCHAR(50) NOT NULL,
                display_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[OK] Created risk_thresholds table")
        
        # 5. Seed default risk rules
        print("Seeding default risk rules...")
        default_rules = [
            ('pii', 'Personally Identifiable Information and sensitive data', 
             '["pii", "personally identifiable", "personal data", "sensitive data"]',
             '["yes", "true", "contains"]', 9),
            ('encryption', 'Data encryption controls',
             '["encrypt", "encryption", "encrypted"]',
             '["no", "false", "not encrypted", "unencrypted"]', 8),
            ('authentication', 'Authentication and access control',
             '["authentication", "access control", "authorized"]',
             '["no", "false", "public", "anyone"]', 9),
            ('public_access', 'Public exposure and external access',
             '["public", "publicly accessible", "external access"]',
             '["yes", "true", "public"]', 8),
            ('monitoring', 'Monitoring and audit trails',
             '["monitor", "logging", "audit trail"]',
             '["no", "false", "not monitored"]', 6),
        ]
        
        for name, desc, keywords, answers, risk_val in default_rules:
            try:
                cursor.execute("""
                    INSERT INTO risk_rules (name, description, keywords, high_risk_answers, risk_value, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (name, desc, keywords, answers, risk_val))
                print(f"  [OK] Added rule: {name}")
            except sqlite3.IntegrityError:
                print(f"  [OK] Rule already exists: {name}")
        
        # 6. Seed default risk thresholds
        print("Seeding default risk thresholds...")
        default_thresholds = [
            ('low', 0, 25, '#22c55e', 1),
            ('medium', 26, 50, '#eab308', 2),
            ('high', 51, 75, '#f97316', 3),
            ('critical', 76, 100, '#ef4444', 4),
        ]
        
        for level, min_s, max_s, color, order in default_thresholds:
            try:
                cursor.execute("""
                    INSERT INTO risk_thresholds (level, min_score, max_score, color, display_order)
                    VALUES (?, ?, ?, ?, ?)
                """, (level, min_s, max_s, color, order))
                print(f"  [OK] Added threshold: {level}")
            except sqlite3.IntegrityError:
                print(f"  [OK] Threshold already exists: {level}")
        
        conn.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        print("\nYou can now start the backend server:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload --port 8000")
        
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Risk Scoring Database Migration")
    print("=" * 60)
    print()
    migrate_database()
