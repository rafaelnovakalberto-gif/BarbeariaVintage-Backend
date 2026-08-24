import sqlite3
import bcrypt

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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            service TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'agendado',
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'funcionario'
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

def create_appointment(client_id, date, time, service):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO appointments (client_id, date, time, service) VALUES (?, ?, ?, ?)",
        (client_id, date, time, service)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_client(client_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_user(username, password, role="funcionario"):
    conn = get_connection()
    password_hash = hash_password(password)
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def verify_login(username, password):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if row is None:
        return None
    if bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return {"username": row["username"], "role": row["role"]}
    return None

def list_users():
    conn = get_connection()
    rows = conn.execute("SELECT id, username, role FROM users").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_user(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def list_clients():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM clients").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def list_appointments():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM appointments ORDER BY date, time").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_client(client_id, name, email, notes):
    conn = get_connection()
    conn.execute(
        "UPDATE clients SET name = ?, email = ?, notes = ? WHERE id = ?",
        (name, email, notes, client_id)
    )
    conn.commit()
    conn.close()

def update_appointment_status(appointment_id, new_status):
    conn = get_connection() 
    conn.execute(
        "UPDATE appointments SET status = ? WHERE id = ?",
        (new_status, appointment_id)
    )
    conn.commit()
    conn.close()

def delete_client(client_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM clients WHERE id = ?",
        (client_id,)  # <- vírgula adicionada aqui
    )
    conn.commit()
    conn.close()

def delete_appointment(appointment_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM appointments WHERE id = ?",
        (appointment_id,)  # <- vírgula adicionada aqui
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    client_id = create_client("João Silva", "joao@example.com", "Prefere corte curto")
    print(f"Cliente criado com id {client_id}")
    appt_id = create_appointment(client_id, "2026-08-25", "14:30", "Corte + Barba")
    print(f"Agendamento criado com id {appt_id}")
    user_id = create_user("admin", "1234")
    print(f"Usuário criado com id {user_id}")
    print("Login com senha certa (1234):", verify_login("admin", "1234"))
    print("Login com senha errada (0000):", verify_login("admin", "0000"))