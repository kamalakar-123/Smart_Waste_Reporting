import os
import sqlite3
from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'waste_report.db')


def get_db():
    # Return a connection with row access by column name
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        g._database = db
    return db


def close_connection(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    # Create DB file and tables if missing
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Users table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TEXT
    );
    ''')

    # Complaints table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        worker_id INTEGER,
        description TEXT NOT NULL,
        image_before_path TEXT NOT NULL,
        image_after_path TEXT,
        latitude REAL,
        longitude REAL,
        status TEXT NOT NULL,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (worker_id) REFERENCES users(id)
    );
    ''')

    conn.commit()
    conn.close()
