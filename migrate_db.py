"""
Database migration script to add firebase_uid column to existing users table
Run this script once to update your existing database
"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'waste_report.db')

def migrate_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        # Check if firebase_uid column exists
        cur.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cur.fetchall()]
        
        if 'firebase_uid' not in columns:
            print("Adding firebase_uid column to users table...")
            # Add column without UNIQUE constraint first (to allow existing rows)
            cur.execute('ALTER TABLE users ADD COLUMN firebase_uid TEXT')
            conn.commit()
            print("✓ Migration successful! firebase_uid column added.")
        else:
            print("✓ Database already up to date. firebase_uid column exists.")
            
    except Exception as e:
        print(f"✗ Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
