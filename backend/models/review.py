from models.db import query, execute, get_connection


def create(order_id, user_id, merchant_id, rating, content):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO reviews (order_id, user_id, merchant_id, rating, content)
               VALUES (?, ?, ?, ?, ?)""",
            (order_id, user_id, merchant_id, rating, content),
        )
        # 更新商家评分
        cursor.execute(
            """UPDATE merchants SET rating = (
               SELECT CAST(AVG(CAST(rating AS DECIMAL(3,1))) AS DECIMAL(2,1))
               FROM reviews WHERE merchant_id = ?
            ) WHERE merchant_id = ?""",
            (merchant_id, merchant_id),
        )
        conn.commit()
        cursor.execute("SELECT @@IDENTITY AS id")
        return cursor.fetchone()[0]


def list_by_merchant(merchant_id):
    return query(
        """SELECT r.*, u.nickname, u.avatar_url
           FROM reviews r
           JOIN users u ON r.user_id = u.user_id
           WHERE r.merchant_id = ?
           ORDER BY r.created_at DESC""",
        (merchant_id,),
    )


def get_by_order(order_id):
    rows = query("SELECT * FROM reviews WHERE order_id = ?", (order_id,))
    return rows[0] if rows else None
