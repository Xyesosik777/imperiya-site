import sqlite3

DB_PATH = "database/users.db"

columns_to_add = {
    "email": "TEXT",
    "uid": "INTEGER",
    "hwid": "TEXT",
    "subscription_end": "TEXT",
    "role": "TEXT DEFAULT 'player'",
    "banned": "INTEGER DEFAULT 0"
}

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Получаем список уже существующих колонок
    c.execute("PRAGMA table_info(users)")
    existing = {row[1] for row in c.fetchall()}

    for column, col_type in columns_to_add.items():
        if column not in existing:
            try:
                c.execute(f"ALTER TABLE users ADD COLUMN {column} {col_type}")
                print(f"[+] Колонка '{column}' добавлена")
            except sqlite3.OperationalError:
                print(f"[-] Колонка '{column}' уже существует")
        else:
            print(f"[-] Колонка '{column}' уже существует")
    conn.commit()
    conn.close()
    print("✅ Обновление базы завершено!")

if __name__ == "__main__":
    migrate()