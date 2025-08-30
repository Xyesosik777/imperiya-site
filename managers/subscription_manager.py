import sqlite3
from datetime import datetime, timedelta

DB_PATH = "database/users.db"

def set_subscription(username, days):
    end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET subscription_end=? WHERE username=?", (end_date, username))
    conn.commit()
    conn.close()

def get_subscription(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT subscription_end FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def is_subscription_active(username):
    end = get_subscription(username)
    if not end:
        return False
    return datetime.now() < datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
