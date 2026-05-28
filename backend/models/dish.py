from models.db import query


def find_by_id(dish_id):
    rows = query("SELECT * FROM dishes WHERE dish_id = ?", (dish_id,))
    return rows[0] if rows else None

