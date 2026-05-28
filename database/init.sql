-- ============================================
-- 外卖点餐系统 数据库初始化脚本
-- 数据库: SQL Server
-- ============================================

-- 1. 创建数据库
IF DB_ID('TakeoutDB') IS NULL
BEGIN
    CREATE DATABASE TakeoutDB;
END
GO

USE TakeoutDB;
GO

-- ============================================
-- 2. 建表
-- ============================================

-- 2.1 用户表
IF OBJECT_ID('reviews', 'U') IS NOT NULL DROP TABLE reviews;
IF OBJECT_ID('order_items', 'U') IS NOT NULL DROP TABLE order_items;
IF OBJECT_ID('orders', 'U') IS NOT NULL DROP TABLE orders;
IF OBJECT_ID('addresses', 'U') IS NOT NULL DROP TABLE addresses;
IF OBJECT_ID('dishes', 'U') IS NOT NULL DROP TABLE dishes;
IF OBJECT_ID('categories', 'U') IS NOT NULL DROP TABLE categories;
IF OBJECT_ID('riders', 'U') IS NOT NULL DROP TABLE riders;
IF OBJECT_ID('merchants', 'U') IS NOT NULL DROP TABLE merchants;
IF OBJECT_ID('users', 'U') IS NOT NULL DROP TABLE users;
GO

CREATE TABLE users (
    user_id      INT IDENTITY(1,1) PRIMARY KEY,
    phone        VARCHAR(11)  NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    nickname     NVARCHAR(50) NOT NULL,
    role         VARCHAR(20) NOT NULL DEFAULT 'customer',  -- customer / rider / merchant
    avatar_url   VARCHAR(255),
    created_at   DATETIME DEFAULT GETDATE()
);
GO

-- 2.2 商家表
CREATE TABLE merchants (
    merchant_id        INT IDENTITY(1,1) PRIMARY KEY,
    user_id            INT NULL,
    name               NVARCHAR(100) NOT NULL,
    logo_url           VARCHAR(255),
    rating             DECIMAL(2,1) DEFAULT 5.0,
    total_sales        INT DEFAULT 0,
    min_delivery_price DECIMAL(8,2) NOT NULL,
    delivery_fee       DECIMAL(5,2) NOT NULL,
    status             TINYINT DEFAULT 1,
    created_at         DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_merchants_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

-- 2.3 菜品分类表
CREATE TABLE categories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    merchant_id INT NOT NULL,
    name        NVARCHAR(50) NOT NULL,
    sort_order  INT DEFAULT 0,
    CONSTRAINT FK_categories_merchant FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
);
GO

-- 2.4 菜品表
CREATE TABLE dishes (
    dish_id       INT IDENTITY(1,1) PRIMARY KEY,
    merchant_id   INT NOT NULL,
    category_id   INT NOT NULL,
    name          NVARCHAR(100) NOT NULL,
    image_url     VARCHAR(255),
    price         DECIMAL(8,2) NOT NULL,
    description   NVARCHAR(500),
    total_sales   INT DEFAULT 0,
    status        TINYINT DEFAULT 1,
    CONSTRAINT FK_dishes_merchant  FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    CONSTRAINT FK_dishes_category  FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
GO

-- 2.5 配送地址表
CREATE TABLE addresses (
    address_id   INT IDENTITY(1,1) PRIMARY KEY,
    user_id      INT NOT NULL,
    contact_name NVARCHAR(50) NOT NULL,
    phone        VARCHAR(11) NOT NULL,
    province     NVARCHAR(50),
    city         NVARCHAR(50),
    district     NVARCHAR(50),
    detail       NVARCHAR(200) NOT NULL,
    is_default   TINYINT DEFAULT 0,
    CONSTRAINT FK_addresses_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

-- 2.6 骑手表 (姓名和电话通过 user_id JOIN users 获取)
CREATE TABLE riders (
    rider_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id  INT NULL,
    status   TINYINT DEFAULT 1,  -- 1空闲 2配送中 0离线
    CONSTRAINT FK_riders_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);
GO

-- 2.7 订单表
CREATE TABLE orders (
    order_id      BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id       INT NOT NULL,
    merchant_id   INT NOT NULL,
    address_id    INT NOT NULL,
    rider_id      INT NULL,
    total_price   DECIMAL(8,2) NOT NULL,
    delivery_fee  DECIMAL(5,2) NOT NULL,
    actual_amount DECIMAL(8,2) NOT NULL,
    status        TINYINT DEFAULT 1,  -- 1待支付 2待接单 3配送中 4已送达 5已取消 6待配送
    remark        NVARCHAR(200),
    paid_at       DATETIME NULL,
    accepted_at   DATETIME NULL,
    delivered_at  DATETIME NULL,
    created_at    DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_orders_user     FOREIGN KEY (user_id)     REFERENCES users(user_id),
    CONSTRAINT FK_orders_merchant FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    CONSTRAINT FK_orders_address  FOREIGN KEY (address_id)  REFERENCES addresses(address_id),
    CONSTRAINT FK_orders_rider    FOREIGN KEY (rider_id)    REFERENCES riders(rider_id)
);
GO

-- 2.8 订单明细表
CREATE TABLE order_items (
    item_id    INT IDENTITY(1,1) PRIMARY KEY,
    order_id   BIGINT NOT NULL,
    dish_id    INT NOT NULL,
    dish_name  NVARCHAR(100) NOT NULL,
    dish_price DECIMAL(8,2) NOT NULL,
    quantity   INT NOT NULL,
    CONSTRAINT FK_order_items_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT FK_order_items_dish  FOREIGN KEY (dish_id)  REFERENCES dishes(dish_id)
);
GO

-- 2.9 评价表
CREATE TABLE reviews (
    review_id   INT IDENTITY(1,1) PRIMARY KEY,
    order_id    BIGINT NOT NULL UNIQUE,
    user_id     INT NOT NULL,
    merchant_id INT NOT NULL,
    rating      TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    content     NVARCHAR(500),
    created_at  DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_reviews_order    FOREIGN KEY (order_id)    REFERENCES orders(order_id),
    CONSTRAINT FK_reviews_user     FOREIGN KEY (user_id)     REFERENCES users(user_id),
    CONSTRAINT FK_reviews_merchant FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
);
GO

-- ============================================
-- 3. 索引
-- ============================================

CREATE INDEX IX_users_phone ON users(phone);
CREATE INDEX IX_orders_user_time    ON orders(user_id, created_at DESC);
CREATE INDEX IX_orders_merchant_status ON orders(merchant_id, status);
CREATE INDEX IX_orders_rider_status ON orders(rider_id, status);
CREATE INDEX IX_dishes_merchant_cat ON dishes(merchant_id, category_id);
CREATE INDEX IX_order_items_order   ON order_items(order_id);
CREATE INDEX IX_reviews_merchant    ON reviews(merchant_id);

GO

-- ============================================
-- 4. 测试数据 (密码均为 123456)
-- ============================================

-- 密码: 123456
-- SHA256: 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92

-- 用户 (customer)
INSERT INTO users (phone, password_hash, nickname, role) VALUES
('13800000001', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', N'张三', 'customer'),
('13800000002', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', N'李四', 'customer');

-- 骑手用户 (rider)
INSERT INTO users (phone, password_hash, nickname, role) VALUES
('13900000001', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', N'王骑手', 'rider'),
('13900000002', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', N'赵骑手', 'rider');

-- 商家用户 (merchant)
INSERT INTO users (phone, password_hash, nickname, role) VALUES
('13800000010', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', N'黄焖鸡商家', 'merchant'),
('13800000020', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', N'奶茶商家', 'merchant');
GO

-- 商家
INSERT INTO merchants (user_id, name, min_delivery_price, delivery_fee) VALUES
((SELECT user_id FROM users WHERE phone = '13800000010'), N'老黄焖鸡米饭', 15.00, 3.00),
((SELECT user_id FROM users WHERE phone = '13800000020'), N'幸福奶茶店',   10.00, 2.00);
GO

-- 分类
INSERT INTO categories (merchant_id, name, sort_order) VALUES
(1, N'热销', 1),
(1, N'主食', 2),
(1, N'小食', 3),
(2, N'热销', 1),
(2, N'奶茶', 2),
(2, N'果茶', 3);
GO

-- 菜品
INSERT INTO dishes (merchant_id, category_id, name, price, description) VALUES
(1, 1, N'黄焖鸡米饭',   22.00, N'大份，含米饭'),
(1, 1, N'黄焖排骨饭',   25.00, N'大份，含米饭'),
(1, 2, N'白米饭',        2.00, N'加一份米饭'),
(1, 3, N'卤蛋',          3.00, N'一颗卤蛋'),
(2, 4, N'珍珠奶茶',      12.00, N'中杯'),
(2, 5, N'椰果奶茶',      13.00, N'中杯'),
(2, 6, N'柠檬水',        8.00,  N'大杯');
GO

-- 地址
INSERT INTO addresses (user_id, contact_name, phone, province, city, district, detail, is_default) VALUES
(1, N'张三', '13800000001', N'广东省', N'广州市', N'天河区', N'五山路100号', 1);
GO

-- 骑手
INSERT INTO riders (user_id) VALUES
((SELECT user_id FROM users WHERE phone = '13900000001')),
((SELECT user_id FROM users WHERE phone = '13900000002'));
GO

PRINT N'>>> 数据库初始化完成 <<<';
GO
