# 外卖管理系统 — E-R 图

> 使用 Mermaid 语法，可在支持 Mermaid 的 Markdown 阅读器中渲染

## 实体关系图 (ER Diagram)

```mermaid
erDiagram
    Users ||--o{ Restaurants : "owns"
    Users ||--o{ Orders : "places (customer)"
    Users ||--o{ Orders : "delivers (rider)"
    Users ||--o{ Reviews : "writes"
    Users ||--o{ Delivery : "performs"

    Restaurants ||--o{ MenuCategories : "has"
    Restaurants ||--o{ MenuItems : "has"
    Restaurants ||--o{ Orders : "receives"
    Restaurants ||--o{ Reviews : "receives"

    MenuCategories ||--o{ MenuItems : "contains"

    Orders ||--o{ OrderItems : "includes"
    Orders ||--|| Delivery : "has"
    Orders ||--|| Reviews : "has"

    MenuItems ||--o{ OrderItems : "referenced_in"

    Users {
        int user_id PK
        string username UK
        string password_hash
        string real_name
        string phone
        string email
        string address
        string role "customer|merchant|rider|admin"
        datetime created_at
    }

    Restaurants {
        int restaurant_id PK
        int owner_id FK
        string name
        string address
        string phone
        string description
        string logo_url
        string status "open|closed"
        datetime created_at
    }

    MenuCategories {
        int category_id PK
        int restaurant_id FK
        string name
        int sort_order
    }

    MenuItems {
        int item_id PK
        int restaurant_id FK
        int category_id FK
        string name
        string description
        decimal price
        string image_url
        string status "available|unavailable"
    }

    Orders {
        int order_id PK
        int customer_id FK
        int restaurant_id FK
        int rider_id FK "nullable"
        string delivery_address
        string status "pending|confirmed|preparing|delivering|delivered|cancelled"
        decimal total_amount
        string note
        datetime created_at
        datetime updated_at
    }

    OrderItems {
        int order_item_id PK
        int order_id FK
        int item_id FK
        int quantity
        decimal unit_price
    }

    Delivery {
        int delivery_id PK
        int order_id FK "unique"
        int rider_id FK
        datetime pickup_time
        datetime delivery_time
        string status "assigned|picked_up|delivered"
    }

    Reviews {
        int review_id PK
        int order_id FK "unique"
        int customer_id FK
        int restaurant_id FK
        tinyint rating "1-5"
        string comment
        datetime created_at
    }
```

## 关系描述

| 关系 | 类型 | 说明 |
|------|------|------|
| Users → Restaurants | 1:N | 一个用户（商家角色）可拥有一个店铺 |
| Users → Orders (customer) | 1:N | 一个顾客可下多个订单 |
| Users → Orders (rider) | 1:N | 一个骑手可配送多个订单 |
| Users → Reviews | 1:N | 一个顾客可写多条评价 |
| Users → Delivery | 1:N | 一个骑手可执行多个配送 |
| Restaurants → MenuCategories | 1:N | 一个商家有多个菜品分类 |
| Restaurants → MenuItems | 1:N | 一个商家有多个菜品 |
| Restaurants → Orders | 1:N | 一个商家接收多个订单 |
| Restaurants → Reviews | 1:N | 一个商家收到多条评价 |
| MenuCategories → MenuItems | 1:N | 一个分类下有多个菜品 |
| Orders → OrderItems | 1:N | 一个订单包含多个菜品明细 |
| Orders → Delivery | 1:1 | 一个订单对应一条配送记录 |
| Orders → Reviews | 1:1 | 一个订单对应一条评价 |
| MenuItems → OrderItems | 1:N | 一个菜品可出现在多个订单明细中 |

## 说明

- 所有表使用 `IDENTITY(1,1)` 自动递增主键
- 金额使用 `DECIMAL(10,2)` 保证精度
- 状态字段使用 `CHECK` 约束限制取值范围
- 关键外键建有索引以提升查询性能
