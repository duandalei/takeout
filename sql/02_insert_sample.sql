-- ============================================================
-- 外卖管理系统 — 示例数据脚本 (v2 — Delivery 已合并到 Orders)
-- 数据库: SQL Server
-- 执行前请确保已运行 01_create_tables.sql
-- 执行方式: 在 SSMS 中按 F5 执行整个文件
-- ============================================================

SET XACT_ABORT ON;
GO

USE TakeoutDB;
GO

-- 清空旧数据（按外键依赖逆序删除）
-- 仅在表中已有数据时才执行清空和重置，避免空表 RESEED 导致的标识值异常
IF EXISTS (SELECT 1 FROM Users)
BEGIN
    DELETE FROM OrderItems;
    DELETE FROM Reviews;
    DELETE FROM Orders;
    DELETE FROM MenuItems;
    DELETE FROM MenuCategories;
    DELETE FROM Restaurants;
    DELETE FROM Users;

    -- 重置自增 ID（有数据时才需要重置）
    DBCC CHECKIDENT ('Users', RESEED, 0);
    DBCC CHECKIDENT ('Restaurants', RESEED, 0);
    DBCC CHECKIDENT ('MenuCategories', RESEED, 0);
    DBCC CHECKIDENT ('MenuItems', RESEED, 0);
    DBCC CHECKIDENT ('Orders', RESEED, 0);
    DBCC CHECKIDENT ('OrderItems', RESEED, 0);
    DBCC CHECKIDENT ('Reviews', RESEED, 0);
END
-- OrderStatuses 保留 (建表时已插入)
GO

-- ============================================================
-- 1. 用户数据 (10 条：4顾客 + 3商家 + 3骑手)
--    密码均为 123456
-- ============================================================
INSERT INTO Users (username, password_hash, real_name, phone, email, address, role) VALUES
('zhangsan',  'scrypt:32768:8:1$AlY3HIt1zzjcymjQ$ac1638c21d2b7f959cf791a3a7e150d0dbfb03dd081b237ed47aa9151142f9ce26b2fdb30c24762c4e3535a9fab8ab914410e6620bcf8563bd0c7e198d86a0a2', N'张三', '13800001001', 'zhangsan@qq.com',   N'北京市朝阳区 xx 路 1 号', 'customer'),
('lisi',      'scrypt:32768:8:1$AlY3HIt1zzjcymjQ$ac1638c21d2b7f959cf791a3a7e150d0dbfb03dd081b237ed47aa9151142f9ce26b2fdb30c24762c4e3535a9fab8ab914410e6620bcf8563bd0c7e198d86a0a2', N'李四', '13800001002', 'lisi@qq.com',       N'北京市海淀区 xx 路 2 号', 'customer'),
('wangwu',    'scrypt:32768:8:1$AlY3HIt1zzjcymjQ$ac1638c21d2b7f959cf791a3a7e150d0dbfb03dd081b237ed47aa9151142f9ce26b2fdb30c24762c4e3535a9fab8ab914410e6620bcf8563bd0c7e198d86a0a2', N'王五', '13800001003', 'wangwu@qq.com',     N'北京市丰台区 xx 路 3 号', 'customer'),
('zhaoliu',   'scrypt:32768:8:1$AlY3HIt1zzjcymjQ$ac1638c21d2b7f959cf791a3a7e150d0dbfb03dd081b237ed47aa9151142f9ce26b2fdb30c24762c4e3535a9fab8ab914410e6620bcf8563bd0c7e198d86a0a2', N'赵六', '13800001004', 'zhaoliu@qq.com',    N'北京市通州区 xx 路 4 号', 'customer'),

('merchant01','scrypt:32768:8:1$AlY3HIt1zzjcymjQ$ac1638c21d2b7f959cf791a3a7e150d0dbfb03dd081b237ed47aa9151142f9ce26b2fdb30c24762c4e3535a9fab8ab914410e6620bcf8563bd0c7e198d86a0a2', N'赵老板', '13900002001', 'zhao@rest.com',   N'北京市东城区', 'merchant'),
('merchant02','scrypt:32768:8:1$AlY3HIt1zzjcymjQ$ac1638c21d2b7f959cf791a3a7e150d0dbfb03dd081b237ed47aa9151142f9ce26b2fdb30c24762c4e3535a9fab8ab914410e6620bcf8563bd0c7e198d86a0a2', N'钱老板', '13900002002', 'qian@rest.com',   N'北京市西城区', 'merchant'),
('merchant03','scrypt:32768:8:1$AlY3HIt1zzjcymjQ$ac1638c21d2b7f959cf791a3a7e150d0dbfb03dd081b237ed47aa9151142f9ce26b2fdb30c24762c4e3535a9fab8ab914410e6620bcf8563bd0c7e198d86a0a2', N'孙老板', '13900002003', 'sun@rest.com',    N'北京市昌平区', 'merchant'),

('rider01',   'scrypt:32768:8:1$AlY3HIt1zzjcymjQ$ac1638c21d2b7f959cf791a3a7e150d0dbfb03dd081b237ed47aa9151142f9ce26b2fdb30c24762c4e3535a9fab8ab914410e6620bcf8563bd0c7e198d86a0a2', N'孙骑手', '13700003001', 'sun1rider@qq.com', N'北京市朝阳区', 'rider'),
('rider02',   'scrypt:32768:8:1$AlY3HIt1zzjcymjQ$ac1638c21d2b7f959cf791a3a7e150d0dbfb03dd081b237ed47aa9151142f9ce26b2fdb30c24762c4e3535a9fab8ab914410e6620bcf8563bd0c7e198d86a0a2', N'周骑手', '13700003002', 'zhou2rider@qq.com', N'北京市海淀区', 'rider'),
('rider03',   'scrypt:32768:8:1$AlY3HIt1zzjcymjQ$ac1638c21d2b7f959cf791a3a7e150d0dbfb03dd081b237ed47aa9151142f9ce26b2fdb30c24762c4e3535a9fab8ab914410e6620bcf8563bd0c7e198d86a0a2', N'吴骑手', '13700003003', 'wu3rider@qq.com', N'北京市丰台区', 'rider');
GO

-- ============================================================
-- 2. 商家数据 (3 家)
--    owner_id 对应 merchant01(5), merchant02(6), merchant03(7)
--    自增 restaurant_id 将为 1, 2, 3
-- ============================================================
INSERT INTO Restaurants (owner_id, name, address, phone, description, status) VALUES
(5, N'好味道川菜馆',  N'北京市东城区王府井大街 100 号', '010-62001001', N'地道川菜，麻辣鲜香，二十年老店', 'open'),
(6, N'京味炸酱面馆',  N'北京市西城区西单北大街 50 号', '010-62001002', N'老北京炸酱面，手工制作，味道正宗', 'open'),
(7, N'幸福烘焙坊',    N'北京市昌平区回龙观东大街 30 号', '010-62001003', N'现烤面包蛋糕，天然酵母发酵', 'open');
GO

-- ============================================================
-- 3. 菜品分类数据
--    restaurant_id 1=川菜馆, 2=炸酱面馆, 3=烘焙坊
--    自增 category_id 将为 1..10
-- ============================================================
INSERT INTO MenuCategories (restaurant_id, name, sort_order) VALUES
-- 川菜馆
(1, N'招牌热菜', 1),
(1, N'凉菜',     2),
(1, N'主食',     3),
(1, N'饮品',     4),
-- 炸酱面馆
(2, N'面食',     1),
(2, N'小菜',     2),
(2, N'饮品',     3),
-- 烘焙坊
(3, N'面包',     1),
(3, N'蛋糕',     2),
(3, N'饮品',     3);
GO

-- ============================================================
-- 4. 菜品数据 (24 条)
--    category_id: 1=招牌热菜,2=凉菜,3=主食,4=饮品 (川菜馆)
--                 5=面食,6=小菜,7=饮品 (炸酱面馆)
--                 8=面包,9=蛋糕,10=饮品 (烘焙坊)
--    自增 item_id 将为 1..24
-- ============================================================
INSERT INTO MenuItems (restaurant_id, category_id, name, description, price, status) VALUES
-- 川菜馆 - 招牌热菜
(1, 1, N'宫保鸡丁', N'鸡肉丁配花生米，酸甜微辣', 32.00, 'available'),
(1, 1, N'麻婆豆腐', N'嫩豆腐配牛肉末，麻辣鲜香', 22.00, 'available'),
(1, 1, N'回锅肉',   N'五花肉配蒜苗，经典川味', 38.00, 'available'),
(1, 1, N'水煮鱼',   N'鲜嫩鱼片，麻辣汤底', 58.00, 'available'),
-- 川菜馆 - 凉菜
(1, 2, N'蒜泥白肉', N'薄切五花肉配蒜泥酱', 28.00, 'available'),
(1, 2, N'口水鸡',   N'口水鸡，麻辣红油风味', 26.00, 'available'),
-- 川菜馆 - 主食
(1, 3, N'蛋炒饭',   N'粒粒分明，香气四溢', 12.00, 'available'),
(1, 3, N'担担面',   N'四川传统担担面', 15.00, 'available'),
-- 川菜馆 - 饮品
(1, 4, N'酸梅汤',   N'冰镇酸梅汤，解辣必备', 8.00,  'available'),
(1, 4, N'王老吉',   N'罐装凉茶', 6.00, 'available'),

-- 炸酱面馆 - 面食
(2, 5, N'传统炸酱面', N'老北京炸酱面配黄瓜丝', 18.00, 'available'),
(2, 5, N'牛肉拉面',   N'兰州风味牛肉拉面', 20.00, 'available'),
(2, 5, N'西红柿鸡蛋面', N'家常西红柿鸡蛋面', 15.00, 'available'),
-- 炸酱面馆 - 小菜
(2, 6, N'拍黄瓜',     N'蒜泥拍黄瓜', 8.00, 'available'),
(2, 6, N'酱牛肉',     N'秘制酱牛肉', 25.00, 'available'),
-- 炸酱面馆 - 饮品
(2, 7, N'豆浆',       N'现磨豆浆', 5.00, 'available'),
(2, 7, N'酸梅汤',     N'冰镇酸梅汤', 8.00, 'available'),

-- 烘焙坊 - 面包
(3, 8,  N'法式可颂',   N'黄油层层折叠，外酥里嫩', 12.00, 'available'),
(3, 8,  N'全麦吐司',   N'健康全麦，早餐首选', 15.00, 'available'),
(3, 8,  N'肉松面包',   N'松软面包配肉松', 10.00, 'available'),
-- 烘焙坊 - 蛋糕
(3, 9,  N'提拉米苏',   N'经典意式提拉米苏', 28.00, 'available'),
(3, 9,  N'芝士蛋糕',   N'纽约风格芝士蛋糕', 25.00, 'available'),
-- 烘焙坊 - 饮品
(3, 10, N'美式咖啡',   N'现磨美式咖啡', 15.00, 'available'),
(3, 10, N'拿铁',       N'意式浓缩配蒸汽牛奶', 18.00, 'available');
GO

-- ============================================================
-- 5. 订单数据 (含配送字段: rider_id, pickup_time, delivery_time)
--    自增 order_id 将为 1..6
-- ============================================================
INSERT INTO Orders (customer_id, restaurant_id, rider_id, delivery_address, status, total_amount, delivery_fee, note, pickup_time, delivery_time) VALUES
(1, 1, 8,  N'北京市朝阳区 xx 路 1 号', 'delivered', 105.00, 5.00, N'少放辣',            '2025-06-01 18:15:00', '2025-06-01 18:45:00'),
(2, 2, 9,  N'北京市海淀区 xx 路 2 号', 'delivered', 49.00,  5.00, N'',                 '2025-06-02 12:05:00', '2025-06-02 12:25:00'),
(3, 3, 10, N'北京市丰台区 xx 路 3 号', 'delivered', 60.00,  5.00, N'',                 '2025-06-03 19:10:00', '2025-06-03 19:40:00'),
(1, 1, NULL, N'北京市朝阳区 xx 路 1 号', 'preparing', 77.00, 5.00, N'不要放糖',         NULL, NULL),
(4, 2, NULL, N'北京市通州区 xx 路 4 号', 'confirmed', 43.00, 5.00, N'',                 NULL, NULL),
(2, 3, NULL, N'北京市海淀区 xx 路 2 号', 'pending',   38.00, 5.00, N'多加糖',           NULL, NULL);
GO

-- ============================================================
-- 6. 订单明细数据
-- ============================================================
INSERT INTO OrderItems (order_id, item_id, quantity, unit_price) VALUES
-- 订单 1 (川菜馆: 宫保鸡丁+麻婆豆腐+回锅肉+酸梅汤)
(1, 1, 1, 32.00),
(1, 2, 1, 22.00),
(1, 3, 1, 38.00),
(1, 9, 1, 8.00),
-- 订单 2 (炸酱面馆: 传统炸酱面x2+拍黄瓜)
(2, 11, 2, 18.00),
(2, 14, 1, 8.00),
-- 订单 3 (烘焙坊: 法式可颂+提拉米苏+芝士蛋糕)
(3, 18, 1, 12.00),
(3, 21, 1, 28.00),
(3, 22, 1, 15.00),
-- 订单 4 (川菜馆: 宫保鸡丁x2+酸梅汤)
(4, 1, 2, 32.00),
(4, 9, 1, 8.00),
-- 订单 5 (炸酱面馆: 传统炸酱面+牛肉拉面)
(5, 11, 1, 18.00),
(5, 12, 1, 20.00),
-- 订单 6 (烘焙坊: 全麦吐司+美式咖啡)
(6, 19, 1, 15.00),
(6, 23, 1, 18.00);
GO

-- ============================================================
-- 7. 评价数据 (restaurant_id 已移除,通过 Orders 关联)
-- ============================================================
INSERT INTO Reviews (order_id, customer_id, rating, comment) VALUES
(1, 1, 5, N'味道非常好，送餐也很快！'),
(2, 2, 4, N'炸酱面很正宗，小菜也不错'),
(3, 3, 5, N'蛋糕新鲜，咖啡好喝，包装精美');
GO

PRINT '=== 示例数据插入完成 ===';
GO
