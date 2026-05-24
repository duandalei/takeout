from models.db import query, execute


def find_free_rider():
    """分配一个空闲骑手"""
    rows = query("SELECT TOP 1 * FROM riders WHERE status = 1 ORDER BY rider_id")
    return rows[0] if rows else None


def set_status(rider_id, status):
    execute("UPDATE riders SET status = ? WHERE rider_id = ?", (status, rider_id))


def get_pending_orders(rider_id):
    """骑手查看待配送订单"""
    return query(
        """SELECT o.*, m.name AS merchant_name, a.detail AS address_detail,
           a.contact_name, a.phone AS address_phone
           FROM orders o
           JOIN merchants m ON o.merchant_id = m.merchant_id
           JOIN addresses a ON o.address_id = a.address_id
           WHERE o.rider_id = ? AND o.status = 3
           ORDER BY o.created_at DESC""",
        (rider_id,),
    )


def find_by_id(rider_id):
    rows = query("SELECT * FROM riders WHERE rider_id = ?", (rider_id,))
    return rows[0] if rows else None


def find_by_user_id(user_id):
    rows = query("SELECT * FROM riders WHERE user_id = ?", (user_id,))
    return rows[0] if rows else None


def get_available_orders():
    """查询所有待配送的订单（status=6, 无骑手接单）"""
    return query(
        """SELECT o.*, m.name AS merchant_name,
           a.contact_name, a.phone, a.province, a.city, a.district, a.detail
           FROM orders o
           JOIN merchants m ON o.merchant_id = m.merchant_id
           JOIN addresses a ON o.address_id = a.address_id
           WHERE o.status = 6 AND o.rider_id IS NULL
           ORDER BY o.created_at DESC"""
    )
