from models.db import query, execute, get_connection


def create(user_id, merchant_id, address_id, total_price, delivery_fee,
           actual_amount, remark, items):
    """下单事务：创建订单 + 订单明细 + 更新销量"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO orders (user_id, merchant_id, address_id, total_price,
               delivery_fee, actual_amount, status, remark)
               VALUES (?, ?, ?, ?, ?, ?, 1, ?)""",
            (user_id, merchant_id, address_id, total_price,
             delivery_fee, actual_amount, remark),
        )
        cursor.execute("SELECT @@IDENTITY AS id")
        order_id = cursor.fetchone()[0]

        for item in items:
            cursor.execute(
                """INSERT INTO order_items (order_id, dish_id, dish_name, dish_price, quantity)
                   VALUES (?, ?, ?, ?, ?)""",
                (order_id, item["dish_id"], item["dish_name"],
                 item["dish_price"], item["quantity"]),
            )
            cursor.execute(
                "UPDATE dishes SET total_sales = ISNULL(total_sales, 0) + ? WHERE dish_id = ?",
                (item["quantity"], item["dish_id"]),
            )

        cursor.execute(
            "UPDATE merchants SET total_sales = ISNULL(total_sales, 0) + 1 WHERE merchant_id = ?",
            (merchant_id,),
        )

        conn.commit()
        return order_id


def find_by_id(order_id):
    rows = query("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    return rows[0] if rows else None


def get_items(order_id):
    return query(
        "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
    )


def list_by_user(user_id):
    return query(
        """SELECT o.*, m.name AS merchant_name
           FROM orders o
           JOIN merchants m ON o.merchant_id = m.merchant_id
           WHERE o.user_id = ?
           ORDER BY o.created_at DESC""",
        (user_id,),
    )


def list_by_merchant(merchant_id, status=None):
    sql = """SELECT o.*, u.nickname AS user_nickname, u.phone AS user_phone,
             a.detail AS address_detail, a.contact_name, a.phone AS contact_phone
             FROM orders o
             JOIN users u ON o.user_id = u.user_id
             JOIN addresses a ON o.address_id = a.address_id
             WHERE o.merchant_id = ?"""
    params = [merchant_id]
    if status is not None:
        sql += " AND o.status = ?"
        params.append(status)
    sql += " ORDER BY o.created_at DESC"
    return query(sql, params)


def update_status(order_id, status, **extra):
    sets = ["status = ?"]
    params = [status]
    for k, v in extra.items():
        if v is not None:
            sets.append(f"{k} = ?")
            params.append(v)
    params.append(order_id)
    execute(
        f"UPDATE orders SET {', '.join(sets)} WHERE order_id = ?",
        params,
    )


def assign_rider(order_id, rider_id):
    execute(
        "UPDATE orders SET rider_id = ? WHERE order_id = ?",
        (rider_id, order_id),
    )


def list_by_rider(rider_id):
    return query(
        """SELECT o.*, m.name AS merchant_name,
           a.contact_name, a.phone, a.province, a.city, a.district, a.detail
           FROM orders o
           JOIN merchants m ON o.merchant_id = m.merchant_id
           JOIN addresses a ON o.address_id = a.address_id
           WHERE o.rider_id = ? AND o.status IN (3, 4)
           ORDER BY o.created_at DESC""",
        (rider_id,),
    )
