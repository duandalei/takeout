# 外卖管理系统 — 建表脚本详解 (`01_create_tables.sql`)

> 本文面向**数据库小白**，用大白话逐行解释这个 SQL 文件在做什么。

---

## 一、这个文件是干什么的？

这个 SQL 文件是**外卖管理系统**的"地基"——它负责在数据库中创建所有需要的**表**（Table）。

你可以把数据库想象成一个 **Excel 工作簿**，里面的每一张**表**就是一个 **Sheet（工作表）**。每个 Sheet 有固定的列（字段），每一行就是一条数据。

这个文件一共创建了 **7 张业务表**，涵盖了外卖系统从用户、商家、菜单、订单到评价的全部核心数据。

---

## 二、运行环境说明

```sql
-- 数据库: SQL Server
```

- 这段脚本运行在 **SQL Server**（微软的数据库产品）上。
- `GO` 是 SQL Server 的**批处理分隔符**，表示"上面这一段可以执行了"，它本身不是 SQL 语句。

> 如果你用的是 MySQL / PostgreSQL，语法会有差异，这段脚本不能直接运行。

---

## 三、创建数据库

```sql
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'TakeoutDB')
    CREATE DATABASE TakeoutDB;
GO
USE TakeoutDB;
GO
```

### 逐行解释

| 行 | 大白话 |
|---|---|
| `IF NOT EXISTS (...)` | "如果还没有这个数据库的话……" |
| `SELECT name FROM sys.databases WHERE name = N'TakeoutDB'` | 去系统表里查一下有没有叫 `TakeoutDB` 的数据库 |
| `CREATE DATABASE TakeoutDB` | 创建一个名叫 `TakeoutDB` 的数据库 |
| `USE TakeoutDB` | 告诉 SQL Server："接下来所有操作都在 `TakeoutDB` 里执行" |

- `N'TakeoutDB'` 中的 `N` 表示这是 **Unicode 字符串**（支持中文等字符），SQL Server 中处理中文时常用。

---

## 四、7 张表逐张详解

### 表 1 — Users（用户表）

```sql
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
```

#### 这张表是干什么的？

这是系统的**用户表**。注意：顾客、商家老板、骑手**共用这一张表**，通过 `role` 字段区分身份。

> 这种"三合一"的设计叫**统一身份认证**，好处是登录逻辑统一，坏处是如果不同角色需要的字段差异很大（比如骑手需要身份证号、车辆信息），后期可能需要额外表来补充。

#### 字段解释

| 字段 | 类型 | 含义 | 大白话 |
|---|---|---|---|
| `user_id` | `INT IDENTITY(1,1)` | 用户ID | **自增主键**，从 1 开始每次 +1，数据库自动生成 |
| `username` | `NVARCHAR(50)` | 用户名 | 登录用，**唯一**（不能重名） |
| `password_hash` | `NVARCHAR(255)` | 密码哈希 | 存在数据库里的从来不是明文密码，是一串算出来的乱码（哈希值） |
| `real_name` | `NVARCHAR(50)` | 真实姓名 | |
| `phone` | `NVARCHAR(20)` | 手机号 | |
| `address` | `NVARCHAR(200)` | 地址 | 顾客的默认送餐地址 |
| `role` | `NVARCHAR(20)` | 角色 | 只能是 `customer`（顾客）、`merchant`（商家）、`rider`（骑手）之一 |
| `created_at` | `DATETIME2` | 注册时间 | 默认取当前时间 `GETDATE()` |

#### 关键语法讲解

| 语法 | 含义 |
|---|---|
| `IDENTITY(1,1)` | 自动编号，从 1 开始，每次增加 1（1, 2, 3, 4...） |
| `PRIMARY KEY` | **主键**：每行数据的唯一身份证，不能重复、不能为空 |
| `NOT NULL` | 必填字段，不能空着 |
| `NULL` | 可选字段，可以不填 |
| `UNIQUE` | 唯一约束，值不能重复（比如用户名） |
| `DEFAULT 'customer'` | 不填时的默认值，新注册的人默认就是顾客 |
| `CHECK (role IN (...))` | 只能填括号里的值，防止出现"超级管理员"这种非法角色 |
| `DEFAULT GETDATE()` | 默认填当前时间 |

#### 建了哪个索引？

```sql
CREATE INDEX IX_Users_Role ON Users(role);
```

**索引**是什么？——索引就像书的**目录**。没有索引，数据库要一行一行翻（全表扫描）；有了索引，直接跳到目标位置。

`IX_Users_Role` 是在 `role` 列上建的索引，因为经常要查"有哪些商家"、"有哪些骑手"，对这个列建索引能加速这类查询。

---

### 表 2 — Restaurants（商家表）

```sql
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
```

#### 这张表是干什么的？

存储**商家/店铺**的基本信息。每个商家有一个**老板**（`owner_id` 关联到 `Users` 表）。

#### 字段解释

| 字段 | 类型 | 含义 |
|---|---|---|
| `restaurant_id` | `INT IDENTITY(1,1)` | 商家ID（主键） |
| `owner_id` | `INT` | 老板的用户ID，**外键**指向 `Users.user_id` |
| `name` | `NVARCHAR(100)` | 店铺名称 |
| `address` | `NVARCHAR(200)` | 店铺地址 |
| `phone` | `NVARCHAR(20)` | 店铺电话 |
| `description` | `NVARCHAR(500)` | 店铺简介 |
| `status` | `NVARCHAR(20)` | 营业状态：`open`（营业中）/ `closed`（休息中） |
| `created_at` | `DATETIME2` | 创建时间 |

#### 🔑 核心概念：外键 (FOREIGN KEY)

```sql
CONSTRAINT FK_Restaurants_Owner
    FOREIGN KEY (owner_id) REFERENCES Users(user_id)
    ON DELETE CASCADE
```

| 关键词 | 含义 |
|---|---|
| `CONSTRAINT FK_Restaurants_Owner` | 给这个约束起个名字 |
| `FOREIGN KEY (owner_id)` | `owner_id` 这一列是外键 |
| `REFERENCES Users(user_id)` | 它的值必须来自 `Users` 表的 `user_id` |
| `ON DELETE CASCADE` | **级联删除**：如果老板的账号被删了，他的商家也自动删除 |

> 🧠 **为什么需要外键？** —— 保证数据不会出乱子。比如你不能把一家店分配给一个不存在的用户（id=99999），数据库会报错拒绝。外键就像数据库里的"法律"，维护着表与表之间的关系。

---

### 表 3 — MenuCategories（菜品分类表）

```sql
CREATE TABLE MenuCategories (
    category_id     INT IDENTITY(1,1) PRIMARY KEY,
    restaurant_id   INT           NOT NULL,
    name            NVARCHAR(50)  NOT NULL,
    sort_order      INT           NOT NULL DEFAULT 0,

    CONSTRAINT FK_Categories_Restaurant
        FOREIGN KEY (restaurant_id) REFERENCES Restaurants(restaurant_id)
        ON DELETE CASCADE
);
```

#### 这张表是干什么的？

每个商家都有自己的菜单分类，比如"招牌菜"、"主食"、"饮品"、"小食"。

#### 字段解释

| 字段 | 含义 |
|---|---|
| `category_id` | 分类ID（主键） |
| `restaurant_id` | 属于哪家店（外键 → `Restaurants`） |
| `name` | 分类名称，如"热卖推荐" |
| `sort_order` | 排序号，数字越小越靠前显示 |

#### 设计要点

每个分类**必须属于一个商家**（`restaurant_id` 是 `NOT NULL` 的外键）。`ON DELETE CASCADE` 表示商家被删了，它的所有分类也自动删掉。

---

### 表 4 — MenuItems（菜品表）

```sql
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
```

#### 这张表是干什么的？

存储每个商家的具体**菜品**信息。每个菜属于一个商家、一个分类。

#### 字段解释

| 字段 | 含义 |
|---|---|
| `item_id` | 菜品ID（主键） |
| `restaurant_id` | 属于哪家店 |
| `category_id` | 属于哪个分类 |
| `name` | 菜名，如"黄焖鸡米饭" |
| `description` | 菜品描述 |
| `price` | 价格，`DECIMAL(10,2)` 表示最多 10 位数，其中 2 位小数 |
| `status` | 状态：`available`（上架）/ `unavailable`（下架） |

#### 🧠 注意

- `price` 有 `CHECK (price >= 0)`，防止出现负价菜品。
- 这个表有**两个外键**：一个指向 `Restaurants`，一个指向 `MenuCategories`。
- `FK_Items_Category` 有 `ON DELETE CASCADE`：删分类时菜品自动跟着删。
- `FK_Items_Restaurant` 没有 CASCADE：删商家时菜品通过分类间接级联删除，避免多路径冲突。

---

### 表 5 — Orders（订单表）

```sql
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
```

#### 这张表是干什么的？

这是系统的**核心表**——订单表。一条订单记录了：谁买的、哪家店的、哪个骑手送的、送到哪、多少钱、当前什么状态。

#### 🧠 设计亮点：Delivery 表已合并

注释里写了"Delivery 已合并到 Orders"。早期设计可能把配送信息单独放一张 `Delivery` 表，后来发现每个订单最多只有一个骑手、一次配送，拆成两张表反而麻烦，就合并了。这是**数据库反范式化**的一个实际例子——当关系是 1:1 时，合在一起更简单。

#### 字段解释

| 字段 | 含义 |
|---|---|
| `order_id` | 订单号（主键） |
| `customer_id` | 顾客ID（外键 → Users） |
| `restaurant_id` | 商家ID（外键 → Restaurants） |
| `rider_id` | 骑手ID（外键 → Users，`NULL` 表示还没分配骑手） |
| `delivery_address` | 送到哪儿 |
| `status` | 订单状态，CHECK 约束限定了 8 种合法值 |
| `total_amount` | 总金额 |
| `delivery_fee` | 配送费，默认 5 元 |
| `note` | 备注，如"不要香菜" |
| `pickup_time` | 骑手取餐时间 |
| `delivery_time` | 送达时间 |
| `created_at` | 下单时间 |

#### 🔑 这个表有 3 个外键

| 外键名 | 指向 | 用途 |
|---|---|---|
| `FK_Orders_Customer` | `Users(user_id)` | 谁买的 |
| `FK_Orders_Restaurant` | `Restaurants(restaurant_id)` | 哪家店的 |
| `FK_Orders_Rider` | `Users(user_id)` | 谁送的（可为空，因为下单时还没分配） |

> 🧠 **`rider_id` 为什么是 `NULL`？** —— 订单刚创建时还没有分配骑手，所以外键允许为空。等商家确认后系统才会指派骑手，那时 `rider_id` 才会被填上。

#### 状态流转

```
pending → confirmed → preparing → ready → assigned → picked_up → delivered
                                                              ↘ cancelled（任何非终态都可以取消）
```

---

### 表 6 — OrderItems（订单明细表）

```sql
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
```

#### 这张表是干什么的？

一张订单可能包含**多个菜品**（比如点了黄焖鸡 ×2 + 可乐 ×1），`OrderItems` 表就是用来拆分这些明细的。

#### 为什么不能把菜名直接写进 Orders 表？

举个例子，一笔订单点了：
- 黄焖鸡米饭 × 2
- 冰可乐 × 1

如果写在 Orders 的一行里，你需要这样存："黄焖鸡米饭×2,冰可乐×1"——这叫**一列存多个值**，数据库很难查询"今天卖了多少份黄焖鸡"。

用 `OrderItems` 拆开：

| order_item_id | order_id | item_id | quantity | unit_price |
|---|---|---|---|---|
| 1 | 100 | 5（黄焖鸡） | 2 | 22.00 |
| 2 | 100 | 12（可乐） | 1 | 5.00 |

这样统计销量、计算金额都很方便。这就是为什么要有**一对多关系**。

#### 字段解释

| 字段 | 含义 |
|---|---|
| `order_item_id` | 明细ID（主键） |
| `order_id` | 属于哪个订单（外键 → Orders） |
| `item_id` | 哪个菜品（外键 → MenuItems） |
| `quantity` | 数量，必须大于 0 |
| `unit_price` | **下单时的单价** |

#### 🧠 为什么存 `unit_price` 而不是从 MenuItems 查？

因为菜品价格会**变动**。今天黄焖鸡 22 元，下个月涨价到 25 元。如果订单明细不记录当时的单价，查历史订单时金额就对不上了。这叫**快照存储**。

---

### 表 7 — Reviews（评价表）

```sql
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
```

#### 这张表是干什么的？

顾客完成订单后可以**评价**。一笔订单只能评价一次（`order_id` 是 `UNIQUE`）。

#### 为什么没有 `restaurant_id`？

注释里说了——`restaurant_id` 已移除，通过 `Orders` 表就能查到订单对应的商家，不需要在评价表里冗余存储。这叫**遵循范式**，避免数据重复。

#### 字段解释

| 字段 | 含义 |
|---|---|
| `review_id` | 评价ID（主键） |
| `order_id` | 评价的是哪个订单（**唯一**，一个订单只能评价一次） |
| `customer_id` | 谁评价的 |
| `rating` | 评分，必须是 1-5 星 |
| `comment` | 文字评价 |

---

## 五、核心数据库概念速成

### 1. 主键 (PRIMARY KEY)

每张表都有一列是主键，特征是：
- **唯一**：不能有两行数据的编号相同
- **非空**：必须有值
- **一张表只有一个主键**

就像你的身份证号，全中国不会重复。

### 2. 外键 (FOREIGN KEY)

外键是**表与表之间的桥梁**。比如 `Orders.customer_id` 必须来自 `Users.user_id`。它的作用是：
- 保证数据完整性（不能引用不存在的用户）
- 表达表之间的关系

### 3. 索引 (INDEX)

索引让查询变快。没有索引，数据库查数据是一行一行翻（全表扫描）。有了索引，就像查字典——直接翻到对应字母那页。

**代价**：索引占磁盘空间，插入/更新/删除数据时索引也要同步维护，会变慢。所以只在经常用来查询的列上建索引。

### 4. 约束 (CONSTRAINT)

| 约束类型 | 说明 | 例子 |
|---|---|---|
| `NOT NULL` | 不能为空 | 用户名必须填 |
| `UNIQUE` | 不能重复 | 用户名不能重复 |
| `CHECK` | 值在指定范围内 | 评分 1-5 |
| `DEFAULT` | 不填时的默认值 | 新用户默认是顾客 |
| `FOREIGN KEY` | 值必须来自另一张表 | 订单的顾客ID必须存在 |

### 5. 数据类型速查

| 类型 | 用途 | 示例 |
|---|---|---|
| `INT` | 整数 | 1, 100, 9999 |
| `TINYINT` | 很小的整数（0-255） | 评分 1-5 |
| `BIT` | 布尔值（0 或 1） | 是/否 |
| `DECIMAL(10,2)` | 精确小数（10位，2位小数） | 22.50 |
| `NVARCHAR(N)` | 变长 Unicode 字符串（最多 N 个字） | 用户名、备注 |
| `DATETIME2` | 日期+时间 | 2024-01-15 18:30:00 |

### 6. 级联删除 (ON DELETE CASCADE)

当父记录被删除时，子记录自动删除。例如：
- 删掉商家 → 自动删掉它的分类
- 删掉订单 → 自动删掉它的订单明细

> ⚠️ 谨慎使用！如果误删了一个用户，可能连带删掉他的商家、分类、订单……数据恢复很难。

---

## 六、整体关系图

```
Users ──────────────┐
  │                 │ (owner_id)
  │                 ▼
  │           Restaurants ──────┐
  │             │   │           │
  │             │   └── MenuCategories
  │             │         │
  │             │       MenuItems
  │             │         │
  │             ▼         ▼
  │           Orders ◄────┘
  │             │   │
  │             │   └── OrderItems
  │             │
  │    ┌────────┘
  │    ▼
  └── Reviews
```

| 关系 | 说明 |
|---|---|
| Users → Restaurants | 一个用户可以拥有多家店 |
| Restaurants → MenuCategories | 一家店有多个分类 |
| MenuCategories → MenuItems | 一个分类有多个菜品 |
| Restaurants + Users + MenuItems → Orders | 订单关联顾客、商家、菜品 |
| Orders → OrderItems | 一个订单有多个明细行 |
| Orders → Reviews | 一个订单有一个评价 |

---

## 七、总结

| 表名 | 作用 | 记录数规模 |
|---|---|---|
| `Users` | 所有用户（顾客/商家/骑手） | 随用户增长 |
| `Restaurants` | 商家信息 | 随商家增长 |
| `MenuCategories` | 菜品分类 | 每家店 5-20 个 |
| `MenuItems` | 菜品 | 每家店 20-200 个 |
| `Orders` | 订单（含配送） | **最多、增长最快** |
| `OrderItems` | 订单明细 | 约为订单数 × 2-3 |
| `Reviews` | 评价 | 约等于已完成订单数 |

这套设计覆盖了外卖系统的核心流程：**用户浏览菜单 → 下单 → 商家接单 → 骑手配送 → 用户评价**。每个环节都有对应的表来存储数据，表与表之间通过外键关联，保证了数据的一致性和完整性。
