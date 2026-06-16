-- ============================================================
-- 外卖管理系统 — 数据库建表脚本 (v3 — 精简版)
-- 数据库: SQL Server
-- ============================================================

-- 创建数据库（如果已存在则跳过）
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'TakeoutDB')
    CREATE DATABASE TakeoutDB;
GO
USE TakeoutDB;
GO

-- ============================================================
-- 1. 用户表 (Users)
-- ============================================================
CREATE TABLE Users (
    user_id         INT IDENTITY(1,1) PRIMARY KEY,
    username        NVARCHAR(50)  NOT NULL UNIQUE,
    password_hash   NVARCHAR(255) NOT NULL,
    real_name       NVARCHAR(50)  NOT NULL,
    phone           NVARCHAR(20)  NOT NULL,
    address         NVARCHAR(200) NULL,
    role            NVARCHAR(20)  NOT NULL DEFAULT 'customer'
                    CHECK (role IN ('customer', 'merchant', 'rider')),
    created_at      DATETIME2     NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_Users_Role ON Users(role);
GO

-- ============================================================
-- 2. 商家表 (Restaurants)
-- ============================================================
CREATE TABLE Restaurants (
    restaurant_id   INT IDENTITY(1,1) PRIMARY KEY,
    owner_id        INT           NOT NULL,
    name            NVARCHAR(100) NOT NULL,
    address         NVARCHAR(200) NOT NULL,
    phone           NVARCHAR(20)  NOT NULL,
    description     NVARCHAR(500) NULL,
    status          NVARCHAR(20)  NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'closed')),
    created_at      DATETIME2     NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_Restaurants_Owner
        FOREIGN KEY (owner_id) REFERENCES Users(user_id)
        ON DELETE CASCADE
);
CREATE INDEX IX_Restaurants_Status ON Restaurants(status);
CREATE INDEX IX_Restaurants_Owner ON Restaurants(owner_id);
GO

-- ============================================================
-- 3. 菜品分类表 (MenuCategories)
-- ============================================================
CREATE TABLE MenuCategories (
    category_id     INT IDENTITY(1,1) PRIMARY KEY,
    restaurant_id   INT           NOT NULL,
    name            NVARCHAR(50)  NOT NULL,
    sort_order      INT           NOT NULL DEFAULT 0,

    CONSTRAINT FK_Categories_Restaurant
        FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id)
        ON DELETE CASCADE
);
CREATE INDEX IX_Categories_Restaurant ON MenuCategories(restaurant_id);
GO

-- ============================================================
-- 4. 菜品表 (MenuItems)
-- ============================================================
CREATE TABLE MenuItems (
    item_id         INT IDENTITY(1,1) PRIMARY KEY,
    restaurant_id   INT           NOT NULL,
    category_id     INT           NOT NULL,
    name            NVARCHAR(100) NOT NULL,
    description     NVARCHAR(500) NULL,
    price           DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    status          NVARCHAR(20)  NOT NULL DEFAULT 'available'
                    CHECK (status IN ('available', 'unavailable')),

    CONSTRAINT FK_Items_Restaurant
        FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id),
    CONSTRAINT FK_Items_Category
        FOREIGN KEY (category_id) REFERENCES MenuCategories(category_id)
        ON DELETE CASCADE
);
CREATE INDEX IX_Items_Restaurant ON MenuItems(restaurant_id);
CREATE INDEX IX_Items_Category ON MenuItems(category_id);
CREATE INDEX IX_Items_Status ON MenuItems(status);
GO

-- ============================================================
-- 5. 订单表 (Orders — 含配送字段)
-- ============================================================
CREATE TABLE Orders (
    order_id         INT IDENTITY(1,1) PRIMARY KEY,
    customer_id      INT           NOT NULL,
    restaurant_id    INT           NOT NULL,
    rider_id         INT           NULL,
    delivery_address NVARCHAR(200) NOT NULL,
    status           NVARCHAR(20)  NOT NULL DEFAULT 'pending'
                     CHECK (status IN (
                         'pending', 'confirmed', 'preparing', 'ready',
                         'assigned', 'picked_up', 'delivered', 'cancelled'
                     )),
    total_amount     DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    delivery_fee     DECIMAL(10,2) NOT NULL DEFAULT 5.00 CHECK (delivery_fee >= 0),
    note             NVARCHAR(500) NULL,
    pickup_time      DATETIME2     NULL,
    delivery_time    DATETIME2     NULL,
    created_at       DATETIME2     NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_Orders_Customer
        FOREIGN KEY (customer_id) REFERENCES Users(user_id),
    CONSTRAINT FK_Orders_Restaurant
        FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id),
    CONSTRAINT FK_Orders_Rider
        FOREIGN KEY (rider_id) REFERENCES Users(user_id)
);
CREATE INDEX IX_Orders_Customer ON Orders(customer_id);
CREATE INDEX IX_Orders_Restaurant ON Orders(restaurant_id);
CREATE INDEX IX_Orders_Rider ON Orders(rider_id);
CREATE INDEX IX_Orders_Status ON Orders(status);
GO

-- ============================================================
-- 6. 订单明细表 (OrderItems)
-- ============================================================
CREATE TABLE OrderItems (
    order_item_id   INT IDENTITY(1,1) PRIMARY KEY,
    order_id        INT           NOT NULL,
    item_id         INT           NOT NULL,
    quantity        INT           NOT NULL CHECK (quantity > 0),
    unit_price      DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),

    CONSTRAINT FK_OrderItems_Order
        FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON DELETE CASCADE,
    CONSTRAINT FK_OrderItems_Item
        FOREIGN KEY (item_id) REFERENCES MenuItems(item_id)
);
CREATE INDEX IX_OrderItems_Order ON OrderItems(order_id);
GO

-- ============================================================
-- 7. 评价表 (Reviews)
-- ============================================================
CREATE TABLE Reviews (
    review_id       INT IDENTITY(1,1) PRIMARY KEY,
    order_id        INT           NOT NULL UNIQUE,
    customer_id     INT           NOT NULL,
    rating          SMALLINT      NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment         NVARCHAR(500) NULL,
    created_at      DATETIME2     NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_Reviews_Order
        FOREIGN KEY (order_id) REFERENCES Orders(order_id)
        ON DELETE CASCADE,
    CONSTRAINT FK_Reviews_Customer
        FOREIGN KEY (customer_id) REFERENCES Users(user_id)
);
CREATE INDEX IX_Reviews_Order ON Reviews(order_id);
GO

PRINT '=== 全部 7 张表创建完成 ===';
GO
