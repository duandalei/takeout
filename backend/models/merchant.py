from models.db import query


def list_all():
    return query(
        "SELECT * FROM merchants WHERE status = 1 ORDER BY monthly_sales DESC"
    )


def find_by_id(merchant_id):
    rows = query("SELECT * FROM merchants WHERE merchant_id = ?", (merchant_id,))
    return rows[0] if rows else None


def get_menu(merchant_id):
    """返回商家菜单，按分类组织"""
    categories = query(
        "SELECT * FROM categories WHERE merchant_id = ? ORDER BY sort_order",
        (merchant_id,),
    )
    dishes = query(
        "SELECT * FROM dishes WHERE merchant_id = ? AND status = 1",
        (merchant_id,),
    )
    # 按 category_id 分组
    menu = {}
    for cat in categories:
        cat_id = cat["category_id"]
        menu[cat_id] = {
            "category_id": cat_id,
            "category_name": cat["name"],
            "sort_order": cat["sort_order"],
            "dishes": [],
        }
    for d in dishes:
        cid = d["category_id"]
        if cid in menu:
            menu[cid]["dishes"].append(d)
    # serializable order
    return sorted(menu.values(), key=lambda x: x["sort_order"])


def find_by_user_id(user_id):
    rows = query("SELECT * FROM merchants WHERE user_id = ?", (user_id,))
    return rows[0] if rows else None


def get_top_by_sales(limit=10):
    return query(
        """SELECT m.*,
           COALESCE(SUM(o.actual_amount), 0) AS revenue
           FROM merchants m
           LEFT JOIN orders o ON m.merchant_id = o.merchant_id AND o.status = 4
              AND o.created_at >= DATEADD(MONTH, -1, GETDATE())
           WHERE m.status = 1
           GROUP BY m.merchant_id, m.name, m.logo_url, m.rating,
                    m.monthly_sales, m.min_delivery_price, m.delivery_fee,
                    m.status, m.created_at
           ORDER BY revenue DESC"""
    )
