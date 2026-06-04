# 外卖管理系统 — 需求分析文档

> 数据库课程设计项目 | SQL Server + Flask

## 1. 系统概述

外卖管理系统是一个基于 Web 的外卖订餐平台，支持顾客在线浏览商家和菜品、下单、追踪订单；商家管理店铺和菜品、处理订单；骑手接单和配送管理。

## 2. 功能需求

### 2.1 用户管理

| 编号 | 功能 | 描述 |
|------|------|------|
| U-01 | 用户注册 | 顾客/商家/骑手角色注册，填写基本信息 |
| U-02 | 用户登录/登出 | 用户名+密码认证，session 管理 |
| U-03 | 角色区分 | 4 种角色：customer（顾客）、merchant（商家）、rider（骑手）、admin（管理员） |
| U-04 | 权限控制 | 不同角色访问不同功能页面 |

### 2.2 商家管理

| 编号 | 功能 | 描述 |
|------|------|------|
| R-01 | 创建店铺 | 商家用户可创建一家店铺 |
| R-02 | 编辑店铺 | 修改店铺名称、地址、电话、描述 |
| R-03 | 店铺状态 | 营业/歇业切换 |
| R-04 | 店铺列表 | 顾客浏览所有营业中的商家 |
| R-05 | 搜索商家 | 按名称/描述搜索 |

### 2.3 菜单管理

| 编号 | 功能 | 描述 |
|------|------|------|
| M-01 | 菜品分类 | 添加/管理菜品分类（如热菜、凉菜、饮品） |
| M-02 | 菜品 CRUD | 添加/编辑/删除菜品 |
| M-03 | 上下架 | 菜品上架/下架控制 |
| M-04 | 菜单浏览 | 顾客按分类浏览商家菜品 |

### 2.4 订单管理

| 编号 | 功能 | 描述 |
|------|------|------|
| O-01 | 下单 | 选择菜品+数量 → 填写地址 → 提交订单 |
| O-02 | 订单状态 | pending → confirmed → preparing → delivering → delivered |
| O-03 | 取消订单 | pending/confirmed 状态可取消 |
| O-04 | 订单列表 | 按角色查看相关订单 |
| O-05 | 订单详情 | 查看订单菜品、状态、配送、评价 |
| O-06 | 订单评价 | 顾客对已完成订单评分(1-5星)+文字评价 |

### 2.5 配送管理

| 编号 | 功能 | 描述 |
|------|------|------|
| D-01 | 骑手接单 | 骑手查看待配送订单并接单 |
| D-02 | 取餐确认 | 骑手到店取餐后确认 |
| D-03 | 送达确认 | 骑手送达后确认完成 |

## 3. 数据字典

### Users（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | INT | PK, IDENTITY | 用户 ID |
| username | NVARCHAR(50) | UK, NOT NULL | 用户名 |
| password_hash | NVARCHAR(255) | NOT NULL | 密码哈希 |
| real_name | NVARCHAR(50) | NOT NULL | 真实姓名 |
| phone | NVARCHAR(20) | NOT NULL | 电话 |
| email | NVARCHAR(100) | NULL | 邮箱 |
| address | NVARCHAR(200) | NULL | 地址 |
| role | NVARCHAR(20) | NOT NULL, CHECK | 角色 |
| created_at | DATETIME2 | NOT NULL, DEFAULT GETDATE() | 创建时间 |

### Restaurants（商家表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| restaurant_id | INT | PK, IDENTITY | 商家 ID |
| owner_id | INT | FK→Users, NOT NULL | 店主 |
| name | NVARCHAR(100) | NOT NULL | 店铺名称 |
| address | NVARCHAR(200) | NOT NULL | 店铺地址 |
| phone | NVARCHAR(20) | NOT NULL | 电话 |
| description | NVARCHAR(500) | NULL | 描述 |
| logo_url | NVARCHAR(255) | NULL | Logo |
| status | NVARCHAR(20) | NOT NULL, CHECK | 状态 |
| created_at | DATETIME2 | NOT NULL | 创建时间 |

### MenuCategories（分类表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| category_id | INT | PK, IDENTITY | 分类 ID |
| restaurant_id | INT | FK→Restaurants | 所属商家 |
| name | NVARCHAR(50) | NOT NULL | 分类名 |
| sort_order | INT | NOT NULL | 排序 |

### MenuItems（菜品表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| item_id | INT | PK, IDENTITY | 菜品 ID |
| restaurant_id | INT | FK→Restaurants | 所属商家 |
| category_id | INT | FK→MenuCategories | 所属分类 |
| name | NVARCHAR(100) | NOT NULL | 菜品名 |
| description | NVARCHAR(500) | NULL | 描述 |
| price | DECIMAL(10,2) | NOT NULL, CHECK >=0 | 价格 |
| image_url | NVARCHAR(255) | NULL | 图片 |
| status | NVARCHAR(20) | NOT NULL, CHECK | 上架/下架 |

### Orders（订单表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| order_id | INT | PK, IDENTITY | 订单 ID |
| customer_id | INT | FK→Users | 顾客 |
| restaurant_id | INT | FK→Restaurants | 商家 |
| rider_id | INT | FK→Users, NULL | 骑手 |
| delivery_address | NVARCHAR(200) | NOT NULL | 配送地址 |
| status | NVARCHAR(20) | NOT NULL, CHECK | 订单状态 |
| total_amount | DECIMAL(10,2) | NOT NULL, CHECK >=0 | 总金额 |
| note | NVARCHAR(500) | NULL | 备注 |
| created_at | DATETIME2 | NOT NULL | 创建时间 |
| updated_at | DATETIME2 | NOT NULL | 更新时间 |

### OrderItems（订单明细表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| order_item_id | INT | PK, IDENTITY | 明细 ID |
| order_id | INT | FK→Orders | 订单 |
| item_id | INT | FK→MenuItems | 菜品 |
| quantity | INT | NOT NULL, CHECK >0 | 数量 |
| unit_price | DECIMAL(10,2) | NOT NULL, CHECK >=0 | 单价 |

### Delivery（配送表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| delivery_id | INT | PK, IDENTITY | 配送 ID |
| order_id | INT | FK→Orders, UK | 订单 |
| rider_id | INT | FK→Users | 骑手 |
| pickup_time | DATETIME2 | NULL | 取餐时间 |
| delivery_time | DATETIME2 | NULL | 送达时间 |
| status | NVARCHAR(20) | NOT NULL, CHECK | 配送状态 |

### Reviews（评价表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| review_id | INT | PK, IDENTITY | 评价 ID |
| order_id | INT | FK→Orders, UK | 订单 |
| customer_id | INT | FK→Users | 顾客 |
| restaurant_id | INT | FK→Restaurants | 商家 |
| rating | TINYINT | NOT NULL, CHECK 1-5 | 评分 |
| comment | NVARCHAR(500) | NULL | 评论 |
| created_at | DATETIME2 | NOT NULL | 创建时间 |

## 4. 业务流程

### 下单流程
```
顾客浏览商家 → 查看菜单 → 选择菜品/数量 → 填写配送地址 → 提交订单 (pending)
→ 商家接单 (confirmed) → 开始备餐 (preparing) → 备好待取 (delivering)
→ 骑手接单 → 骑手取餐 (picked_up) → 骑手送达 (delivered) → 顾客评价
```

### 订单状态机
```
pending ──→ confirmed ──→ preparing ──→ delivering ──→ delivered
   │             │
   └─────────────┴──→ cancelled
```
