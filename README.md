# 外卖管理系统

数据库课程设计项目 — 基于 SQL Server + Flask 的 Web 外卖订餐平台。

## 功能模块

| 模块 | 说明 |
|------|------|
| 用户管理 | 注册 / 登录 / 3 种角色：顾客、商家、骑手 |
| 商家管理 | 开店 / 编辑 / 营业歇业切换 / 搜索浏览 |
| 菜单管理 | 菜品分类 CRUD / 菜品 CRUD / 上下架 |
| 订单管理 | 下单 / 接单 / 状态流转 / 配送 / 评价 |

## 技术栈

| 层 | 技术 |
|---|------|
| 数据库 | SQL Server |
| 驱动 | pyodbc + ODBC Driver 17 |
| ORM | SQLAlchemy 2.x |
| 后端 | Flask 3.x (Python 3.10) |
| 前端 | Jinja2 + Bootstrap 5 + Bootstrap Icons |
| 表单 | WTForms + Flask-WTF |
| 密码 | Werkzeug scrypt 哈希 |

## 架构

```
请求 → Blueprint(路由) → Domain(领域逻辑) → Models(数据模型) → SQL Server
                ↓
           Templates → 响应
```

- **Routes** 只做 HTTP 适配：解析请求、调用领域模块、渲染响应
- **Domain** 封装核心逻辑，与 Flask 解耦，可脱离 HTTP 测试
- **Models** 7 张表的 SQLAlchemy ORM 映射（Delivery 表已合并到 Orders）

### 订单状态机

```
pending ──→ confirmed ──→ preparing ──→ ready
   │            │                         │
   │            │                      (骑手接单)
   │            │                         ↓
   │            │                      assigned
   │            │                         │
   │            │                   (骑手取餐/送达)
   │            │                         ↓
   │            │                   picked_up → delivered
   │            │
   └────────────┴──→ cancelled
```

状态流转集中在 `app/domain/order_state.py`，一个接口覆盖全部 8 种状态转换。

### 鉴权体系

统一鉴权装饰器 `@require(role=..., owns=...)` 在 `app/domain/auth.py` 中。一次声明即完成登录检查、角色校验、资源所有权验证，替代了散落在各路由文件中的 `@login_required + @role_required + 行内 ownership 查询` 模式。

## 快速开始

### 1. 环境准备

- SQL Server（Express 或以上）
- Anaconda（已创建 `takeout` 环境，Python 3.10）
- ODBC Driver 17 for SQL Server

### 2. 安装依赖

```bash
conda activate takeout
pip install -r requirements.txt
```

### 3. 配置数据库

编辑 `app/config.py`，默认 Windows 身份验证连接本地 SQL Server：

```python
DB_SERVER = '.'          # .  = 本地默认实例
DB_NAME   = 'TakeoutDB'  # 数据库名
```

也支持环境变量：`DB_SERVER`、`DB_NAME`、`SECRET_KEY`。配送费通过 `DELIVERY_FEE` 类变量配置（默认 ¥5.00）。

### 4. 建库建表

在 SSMS 中依次执行：

1. `sql/01_create_tables.sql` — 建库 + 7 张数据表 + 1 张状态查找表
2. `sql/02_insert_sample.sql` — 示例数据（10 个用户、3 家店、24 个菜品、6 个订单）

> 如果已有旧库，先 `DROP DATABASE TakeoutDB;` 再执行。`02_insert_sample.sql` 会自动检测已有数据并清空后重新插入。

### 5. 启动

```bash
python run.py
```

浏览器访问 **http://127.0.0.1:5000**

> Windows 下可双击 `start.bat` 一键启动。

## 测试账号

所有账号密码统一为 **`123456`**

| 用户名 | 角色 | 真实姓名 | 体验流程 |
|--------|------|----------|----------|
| `zhangsan` | 顾客 | 张三 | 浏览商家 → 下单 → 查看订单 → 评价 |
| `merchant01` | 商家 | 赵老板 | 管理店铺 → 编辑菜品 → 处理订单 |
| `rider01` | 骑手 | 孙骑手 | 查看待接订单 → 接单 → 取餐 → 送达 |

示例数据中共有 10 个用户：4 位顾客、3 位商家、3 位骑手。

## 项目结构

```
takeout/
├── sql/
│   ├── 01_create_tables.sql       # 建库建表（含状态查找表初始数据）
│   └── 02_insert_sample.sql       # 示例数据（自动检测重复执行）
├── app/
│   ├── __init__.py                # Flask 工厂函数（create_app）
│   ├── config.py                  # 数据库配置（含 DELIVERY_FEE）
│   ├── forms.py                   # WTForms 表单（7 个表单类）
│   ├── domain/
│   │   ├── __init__.py            # 导出 OrderState, Authorization, require
│   │   ├── order_state.py         # 订单状态机（深度模块）
│   │   └── auth.py                # 统一鉴权装饰器 @require()
│   ├── models/
│   │   ├── __init__.py            # 模型导出
│   │   └── models.py              # 8 个 SQLAlchemy 实体（含 OrderStatus）
│   ├── routes/
│   │   ├── auth.py                # 注册 / 登录 / 登出
│   │   ├── restaurant.py          # 商家管理（含分类管理）
│   │   ├── menu.py                # 菜品 CRUD / 上下架
│   │   ├── order.py               # 订单管理（含状态流转、评价）
│   │   └── delivery.py            # 配送管理（接单/取餐/送达）
│   ├── templates/                 # Jinja2 模板（17 个）
│   │   ├── auth/                  # login.html, register.html
│   │   ├── restaurant/            # list, detail, my, create, edit, category_form
│   │   ├── menu/                  # form.html
│   │   ├── order/                 # create, list, detail, review
│   │   ├── delivery/              # available, my
│   │   ├── base.html              # 基础布局（导航栏 + 页脚）
│   │   └── index.html             # 首页
│   └── static/style.css           # 自定义样式
├── docs/
│   └── agents/                    # Agent 配置指引（issue-tracker, triage-labels, domain）
├── CLAUDE.md                      # Claude Code 项目指令
├── PRODUCT.md                     # 产品定义与设计原则
├── requirements.txt               # Python 依赖
├── run.py                         # 启动入口
├── start.bat                      # Windows 一键启动
└── 系统设计文档.md / .pdf          # 完整系统设计文档（功能结构图、E-R 图、状态流转、表结构）
```

## 数据库 E-R 概览

```
Users ──1:N── Restaurants ──1:N── MenuCategories ──1:N── MenuItems
  │              │                                         │
  │              │                                         │
  └──1:N── Orders ───1:N── OrderItems ─────────────────────┘
        │        │
        │        └──1:1── Reviews ──N:1── Users (customer)
        │
        └──N:1── Users (rider)
```

8 张数据表（7 张业务表 + 1 张状态查找表）：

| 表 | 说明 |
|----|------|
| `OrderStatuses` | 订单状态查找表（8 种状态 + 终态标记） |
| `Users` | 用户（顾客、商家、骑手） |
| `Restaurants` | 商家店铺 |
| `MenuCategories` | 菜品分类 |
| `MenuItems` | 菜品 |
| `Orders` | 订单（含配送字段：rider_id、pickup_time、delivery_time） |
| `OrderItems` | 订单明细（快照下单时单价） |
| `Reviews` | 评价（restaurant_id 已移除，通过 Orders 关联查询） |

> **v2 架构变更**：Delivery（配送表）已合并到 Orders 表中。原 `rider_id`、`pickup_time`、`delivery_time` 字段现在直接在 Orders 表上。Reviews 表不再存 `restaurant_id`，通过 `Orders.restaurant_id` 获取。

## 设计文档

完整系统设计文档见 `系统设计文档.md`（含 Mermaid 图表：功能结构图、E-R 图、状态流转图、全部 8 张表结构定义）。PDF 版本见 `系统设计文档.pdf`。

产品定义与设计原则见 `PRODUCT.md`。
