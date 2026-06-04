-- ============================================================
-- 外卖管理系统 — 常见查询示例
-- 数据库: SQL Server
-- 用于课程设计报告中的 SQL 查询部分
-- ============================================================

USE TakeoutDB;
GO

-- ============================================================
-- 1. 查询所有营业中的商家
-- ============================================================
SELECT restaurant_id, name, address, phone, description
FROM Restaurants
WHERE status = 'open'
ORDER BY name;

-- ============================================================
-- 2. 查询某商家的在售菜品（含分类）
-- ============================================================
SELECT mc.name AS category_name, mi.name AS item_name, mi.price, mi.description
FROM MenuItems mi
JOIN MenuCategories mc ON mi.category_id = mc.category_id
WHERE mi.restaurant_id = 1
  AND mi.status = 'available'
ORDER BY mc.sort_order, mi.name;

-- ============================================================
-- 3. 查询某用户的订单历史
-- ============================================================
SELECT o.order_id,
       r.name          AS restaurant_name,
       o.total_amount,
       o.status,
       o.created_at,
       d.status        AS delivery_status,
       rev.rating,
       rev.comment
FROM Orders o
JOIN Restaurants r ON o.restaurant_id = r.restaurant_id
LEFT JOIN Delivery d   ON o.order_id = d.order_id
LEFT JOIN Reviews rev  ON o.order_id = rev.order_id
WHERE o.customer_id = 1
ORDER BY o.created_at DESC;

-- ============================================================
-- 4. 统计每个商家的订单数量和总收入
-- ============================================================
SELECT r.restaurant_id,
       r.name,
       COUNT(o.order_id)       AS order_count,
       ISNULL(SUM(o.total_amount), 0) AS total_revenue,
       ISNULL(AVG(rev.rating), 0)     AS avg_rating
FROM Restaurants r
LEFT JOIN Orders o   ON r.restaurant_id = o.restaurant_id
                       AND o.status != 'cancelled'
LEFT JOIN Reviews rev ON o.order_id = rev.order_id
GROUP BY r.restaurant_id, r.name
ORDER BY total_revenue DESC;

-- ============================================================
-- 5. 查询热门菜品 TOP 5（按销量）
-- ============================================================
SELECT TOP 5
       mi.item_id,
       mi.name        AS item_name,
       r.name         AS restaurant_name,
       SUM(oi.quantity) AS total_sold,
       SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM OrderItems oi
JOIN MenuItems mi   ON oi.item_id = mi.item_id
JOIN Restaurants r  ON mi.restaurant_id = r.restaurant_id
JOIN Orders o       ON oi.order_id = o.order_id
WHERE o.status != 'cancelled'
GROUP BY mi.item_id, mi.name, r.name
ORDER BY total_sold DESC;

-- ============================================================
-- 6. 查询骑手的配送统计
-- ============================================================
SELECT u.user_id,
       u.real_name,
       COUNT(d.delivery_id)                        AS total_deliveries,
       COUNT(CASE WHEN d.status = 'delivered' THEN 1 END) AS completed,
       AVG(DATEDIFF(MINUTE, o.created_at, d.delivery_time)) AS avg_delivery_minutes
FROM Users u
JOIN Delivery d   ON u.user_id = d.rider_id
JOIN Orders o     ON d.order_id = o.order_id
WHERE u.role = 'rider'
GROUP BY u.user_id, u.real_name
ORDER BY completed DESC;

-- ============================================================
-- 7. 查询各状态订单数量（仪表盘用）
-- ============================================================
SELECT status, COUNT(*) AS count
FROM Orders
GROUP BY status
ORDER BY
    CASE status
        WHEN 'pending'    THEN 1
        WHEN 'confirmed'  THEN 2
        WHEN 'preparing'  THEN 3
        WHEN 'delivering' THEN 4
        WHEN 'delivered'  THEN 5
        WHEN 'cancelled'  THEN 6
    END;

-- ============================================================
-- 8. 查询某用户购物车/当前未完成订单
-- ============================================================
SELECT o.order_id,
       r.name AS restaurant_name,
       o.status,
       o.total_amount,
       STRING_AGG(mi.name + ' x' + CAST(oi.quantity AS NVARCHAR), '; ') AS items
FROM Orders o
JOIN Restaurants r  ON o.restaurant_id = r.restaurant_id
JOIN OrderItems oi  ON o.order_id = oi.order_id
JOIN MenuItems mi   ON oi.item_id = mi.item_id
WHERE o.customer_id = 1
  AND o.status NOT IN ('delivered', 'cancelled')
GROUP BY o.order_id, r.name, o.status, o.total_amount;

-- ============================================================
-- 9. 插入新订单的存储过程示例
-- ============================================================
-- CREATE PROCEDURE sp_CreateOrder
--     @customer_id INT,
--     @restaurant_id INT,
--     @delivery_address NVARCHAR(200),
--     @note NVARCHAR(500) = NULL,
--     @items_json NVARCHAR(MAX)  -- [{"item_id":1,"quantity":2}, ...]
-- AS
-- BEGIN
--     ...
-- END;
-- GO

-- ============================================================
-- 10. 更新订单状态触发器示例（更新 updated_at）
-- ============================================================
-- CREATE TRIGGER trg_Orders_UpdateStatus
-- ON Orders
-- AFTER UPDATE
-- AS
-- BEGIN
--     IF UPDATE(status)
--     BEGIN
--         UPDATE Orders
--         SET updated_at = GETDATE()
--         WHERE order_id IN (SELECT order_id FROM inserted);
--     END
-- END;
-- GO

PRINT '=== 常见查询示例结束 ===';
GO
