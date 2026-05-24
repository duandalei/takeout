from models.db import query, execute


def list_by_user(user_id):
    return query(
        "SELECT * FROM addresses WHERE user_id = ? ORDER BY is_default DESC",
        (user_id,),
    )


def find_by_id(address_id):
    rows = query("SELECT * FROM addresses WHERE address_id = ?", (address_id,))
    return rows[0] if rows else None


def create(user_id, contact_name, phone, province, city, district, detail, is_default=0):
    # 如果设为默认，先取消其他默认
    if is_default:
        execute(
            "UPDATE addresses SET is_default = 0 WHERE user_id = ?", (user_id,)
        )
    sql = """INSERT INTO addresses
             (user_id, contact_name, phone, province, city, district, detail, is_default)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    return execute(
        sql, (user_id, contact_name, phone, province, city, district, detail, is_default)
    )


def update(address_id, user_id, **kwargs):
    sets = []
    params = []
    for k, v in kwargs.items():
        if v is not None:
            sets.append(f"{k} = ?")
            params.append(v)
    if not sets:
        return
    params.append(address_id)
    params.append(user_id)
    execute(
        f"UPDATE addresses SET {', '.join(sets)} WHERE address_id = ? AND user_id = ?",
        params,
    )


def delete(address_id, user_id):
    execute(
        "DELETE FROM addresses WHERE address_id = ? AND user_id = ?",
        (address_id, user_id),
    )
