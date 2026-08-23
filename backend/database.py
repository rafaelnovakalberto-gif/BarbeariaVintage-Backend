import sqlite3

DATABASE_NAME = "barbearia.db"

def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def create_client(name, email, notes):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO clients (name, email, notes) VALUES (?, ?, ?)",
        (name, email, notes)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id