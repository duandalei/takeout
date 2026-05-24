from models.db import query, execute


def find_by_phone(phone):
    rows = query("SELECT * FROM users WHERE phone = ?", (phone,))
    return rows[0] if rows else None


def find_by_id(user_id):
    rows = query("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return rows[0] if rows else None


def create(phone, password_hash, nickname, role='customer'):
    sql = "INSERT INTO users (phone, password_hash, nickname, role) VALUES (?, ?, ?, ?)"
    return execute(sql, (phone, password_hash, nickname, role))
