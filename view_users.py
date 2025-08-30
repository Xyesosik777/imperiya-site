import sqlite3

DB_PATH = "database/users.db"

def view_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, email, uid, hwid, subscription_end, role, banned FROM users")
    rows = c.fetchall()
    conn.close()

    print(f"{'USERNAME':<15}{'EMAIL':<25}{'UID':<10}{'HWID':<20}{'SUBSCRIPTION END':<18}{'ROLE':<10}{'BANNED'}")
    print("-" * 110)
    for row in rows:
        banned = "Да" if row[6] else "Нет"
        print(f"{row[0]:<15}{row[1] or '-':<25}{row[2] or '-':<10}{row[3] or '-':<20}{row[4] or '-':<18}{row[5] or '-':<10}{banned}")

if __name__ == "__main__":
    view_all_users()