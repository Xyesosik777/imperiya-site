import sqlite3

DB_PATH = "database/users.db"


def set_hwid(username: str, hwid: str | None):
    """Записывает HWID для пользователя (или сбрасывает, если hwid=None)"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE users SET hwid=? WHERE username=?", (hwid, username))
    conn.commit()
    conn.close()


def get_hwid(username: str) -> str:
    """
    Возвращает HWID пользователя.
    Если в БД ничего нет или поле пустое — «не привязан».
    """
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT hwid FROM users WHERE username=?", (username,)).fetchone()
    conn.close()

    if not row or row[0] in (None, "", "NULL"):
        return "не привязан"
    return row[0]