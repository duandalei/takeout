# 外卖管理系统

数据库课程设计项目 — 基于 SQL Server + Flask 的 Web 外卖订餐平台。

## 功能模块

| 模块 | 说明 |
|------|------|
| 用户管理 | 注册 / 登录 / 4 种角色：顾客、商家、骑手、管理员 |
| 商家管理 | 开店 / 编辑 / 营业歇业切换 / 搜索浏览 |
| 菜单管理 | 菜品分类 / 菜品 CRUD / 上下架 |
| 订单管理 | 下单 / 接单 / 状态流转 / 评价 |
| 配送管理 | 骑手接单 / 取餐确认 / 送达确认 |

## 技术栈

| 层 | 技术 |
|---|------|
| 数据库 | SQL Server |
| 驱动 | pyodbc + ODBC Driver 17 |
| ORM | SQLAlchemy |
| 后端 | Flask (Python 3.10) |
| 前端 | Jinja2 + Bootstrap 5 |
| 密码 | Werkzeug scrypt 哈希 |

## 快速开始

### 1. 环境准备

- SQL Server（Express 或以上）
- Anaconda（已创建 `takeout` 环境）
- ODBC Driver 17 for SQL Server

### 2. 安装依赖

```bash
conda activate takeout
pip install -r requirements.txt
```

### 3. 配置数据库连接

编辑 `app/config.py`，默认使用 Windows 身份验证连接本地 SQL Server：

```python
DB_SERVER = '.'          # .  = 本地默认实例
DB_NAME   = 'TakeoutDB'  # 数据库名
```

### 4. 建库建表

在 SSMS 中依次执行：

1. `sql/01_create_tables.sql` — 创建数据库 + 8 张表
2. `sql/02_insert_sample.sql` — 插入示例数据

### 5. 启动

```bash
python run.py
```

浏览器访问 **http://127.0.0.1:5000**

> 也可双击 `start.bat` 一键启动

## 测试账号

所有账号密码统一为 **`123456`**

| 用户名 | 角色 | 体验流程 |
|--------|------|----------|
| `zhangsan` | 顾客 | 浏览商家 → 下单 → 查看订单 → 评价 |
| `merchant01` | 商家 | 管理店铺 → 编辑菜品 → 处理订单 |
| `rider01` | 骑手 | 接单 → 取餐 → 送达 |
| `admin01` | 管理员 | 全部权限 |

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
│   ├── models/
│   │   └── models.py            # 8 个 SQLAlchemy 实体
│   ├── routes/
│   │   ├── auth.py              # 注册 / 登录 / 登出
│   │   ├── restaurant.py        # 商家管理
│   │   ├── menu.py              # 菜品管理
│   │   ├── order.py             # 订单管理
│   │   └── delivery.py          # 配送管理
│   ├── templates/               # Jinja2 模板 (17 个)
│   └── static/style.css         # 自定义样式
├── docs/
│   ├── requirements.md          # 需求分析 + 数据字典
│   ├── er_diagram.md            # Mermaid E-R 图
│   └── user_manual.md           # 用户使用手册
├── run.py                       # 启动入口
├── start.bat                    # Windows 一键启动
└── requirements.txt             # Python 依赖
```

## 数据库 E-R 概览

```
Users ──1:N── Restaurants ──1:N── MenuCategories ──1:N── MenuItems
  │              │                                         │
  │              │                                         │
  └──1:N── Orders ───1:N── OrderItems ─────────────────────┘
              │  │
              │  └──1:1── Delivery ──N:1── Users (rider)
              │
              └──1:1── Reviews ──N:1── Users (customer)
```

## 订单状态机

```
pending → confirmed → preparing → delivering → delivered
   │          │
   └──────────┴──→ cancelled
```
