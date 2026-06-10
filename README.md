# 外卖管理系统

数据库课程设计项目 — 基于 SQL Server + Flask 的 Web 外卖订餐平台。

## 功能模块

| 模块 | 说明 |
|------|------|
| 用户管理 | 注册 / 登录 / 3 种角色：顾客、商家、骑手 |
| 商家管理 | 开店 / 编辑 / 营业歇业切换 / 搜索浏览 |
| 菜单管理 | 菜品分类 / 菜品 CRUD / 上下架 |
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
- **Models** 7 张表的 SQLAlchemy ORM 映射

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

也支持环境变量：`DB_SERVER`、`DB_NAME`、`SECRET_KEY`。

### 4. 建库建表

在 SSMS 中依次执行：

1. `sql/01_create_tables.sql` — 建库 + 7 张表 + 状态查找表
2. `sql/02_insert_sample.sql` — 示例数据（11 个用户、3 家店、24 个菜品、6 个订单）

> 如果已有旧库，先 `DROP DATABASE TakeoutDB;` 再执行。

### 5. 启动

```bash
python run.py
```

浏览器访问 **http://127.0.0.1:5000**

> Windows 下可双击 `start.bat` 一键启动。

## 测试账号

所有账号密码统一为 **`123456`**

| 用户名 | 角色 | 体验流程 |
|--------|------|----------|
| `zhangsan` | 顾客 | 浏览商家 → 下单 → 查看订单 → 评价 |
| `merchant01` | 商家 | 管理店铺 → 编辑菜品 → 处理订单 |
| `rider01` | 骑手 | 接单 → 取餐 → 送达 |

## 项目结构

```
takeout/
├── sql/
│   ├── 01_create_tables.sql     # 建库建表
│   ├── 02_insert_sample.sql     # 示例数据
│   └── 03_queries.sql           # 常用查询示例
├── app/
│   ├── __init__.py              # Flask 工厂函数
│   ├── config.py                # 数据库配置
│   ├── forms.py                 # WTForms 表单
│   ├── domain/
│   │   ├── __init__.py          # 导出 OrderState, Authorization, require
│   │   ├── order_state.py       # 订单状态机（深度模块）
│   │   └── auth.py              # 统一鉴权装饰器
│   ├── models/
│   │   ├── __init__.py          # 模型导出
│   │   └── models.py            # 7 个 SQLAlchemy 实体
│   ├── routes/
│   │   ├── auth.py              # 注册 / 登录 / 登出
│   │   ├── restaurant.py        # 商家管理
│   │   ├── menu.py              # 菜品管理
│   │   ├── order.py             # 订单管理（含状态流转）
│   │   └── delivery.py          # 配送管理
│   ├── templates/               # Jinja2 模板 (17 个)
│   └── static/style.css         # 自定义样式
├── docs/
│   └── agents/                  # Agent 配置指引
├── requirements.txt             # Python 依赖
├── run.py                       # 启动入口
└── start.bat                    # Windows 一键启动
```

## 数据库 E-R 概览

```
Users ──1:N── Restaurants ──1:N── MenuCategories ──1:N── MenuItems
  │              │                                         │
  │              │                                         │
  └──1:N── Orders ───1:N── OrderItems ─────────────────────┘
              │  │
              │  └──1:1── Reviews ──N:1── Users (customer)
              │
              └──N:1── Users (rider)
```

7 张数据表 + 1 张状态查找表：

| 表 | 说明 |
|----|------|
| `Users` | 用户（顾客、商家、骑手） |
| `Restaurants` | 商家店铺 |
| `MenuCategories` | 菜品分类 |
| `MenuItems` | 菜品 |
| `Orders` | 订单（含配送字段：rider_id、pickup_time、delivery_time） |
| `OrderItems` | 订单明细 |
| `Reviews` | 评价 |
| `OrderStatuses` | 订单状态查找表 |

## 常见查询

参考 `sql/03_queries.sql`，包含：

- 营业商家列表 / 菜品浏览
- 订单历史（含配送、评价）
- 商家营收统计（含评分）
- 热门菜品 TOP 5
- 骑手配送统计
- 仪表盘（各状态订单数）
