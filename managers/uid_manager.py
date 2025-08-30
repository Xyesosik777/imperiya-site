import sqlite3
import random

DB_PATH = "database/users.db"

def generate_uid():
    return str(random.randint(100000, 999999))  # 6 цифр

def assign_uid(username, email):
    uid = generate_uid()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET uid=?, email=? WHERE username=?", (uid, email, username))
    conn.commit()
    conn.close()
    return uid

def get_uid(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT uid FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
