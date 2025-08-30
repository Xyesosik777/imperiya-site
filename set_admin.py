import sqlite3

DB_PATH = "database/users.db"
uid = 444690  # твой UID

conn = sqlite3.connect(DB_PATH)
conn.execute("UPDATE users SET role='admin' WHERE uid=?", (uid,))
conn.commit()
conn.close()
print("Роль admin выдана UID", uid)