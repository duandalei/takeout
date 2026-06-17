# 🍱 外卖管理系统

> 数据库课程设计项目 — 一个完整的外卖订餐 Web 平台，覆盖从浏览、下单到配送、评价的全业务流程。

## 概述

外卖管理系统是一个基于 Flask 的 Web 应用，演示了数据库设计与 Web 开发的实际结合。系统围绕 **7 张数据表** 构建，支撑 **3 种角色**（顾客、商家、骑手）协作完成外卖业务的完整闭环。

- **顾客** — 浏览商家与菜单、下单、跟踪订单状态、评价已完成的订单
- **商家** — 开店与管理店铺、维护菜品分类与菜品、处理订单（接单 → 备餐 → 备好待取）
- **骑手** — 查看可接配送订单、接单、标记取餐与送达

---

## 快速开始

### 环境要求

| 组件 | 说明 |
|------|------|
| 数据库 | SQL Server（Express 或以上） |
| Python | 3.10（推荐使用 Anaconda 管理） |
| ODBC 驱动 | ODBC Driver 17 for SQL Server |
| 包管理 | pip + conda |

### 1. 克隆项目

```bash
git clone <repo-url>
cd takeout
```

### 2. 安装依赖

```bash
conda activate takeout
pip install -r requirements.txt
```

### 3. 配置数据库

编辑 `app/config.py`，默认使用 Windows 身份验证连接本地 SQL Server：

```python
DB_SERVER = '.'          # . = 本地默认实例
DB_NAME   = 'TakeoutDB'  # 数据库名称
```

也可以通过环境变量配置：

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `DB_SERVER` | SQL Server 实例地址 | `.` |
| `DB_NAME` | 数据库名称 | `TakeoutDB` |
| `SECRET_KEY` | Flask 密钥 | 内置默认值 |

### 4. 初始化数据库

在 SSMS 中依次执行 `sql/` 目录下的脚本：

1. **`01_create_tables.sql`** — 创建数据库 + 7 张数据表 + 1 张状态查找表
2. **`02_insert_sample.sql`** — 插入示例数据（10 个用户、3 家店铺、24 个菜品、6 个订单）

> 如需重建：先在 SSMS 中执行 `DROP DATABASE TakeoutDB;`，再重新执行上述脚本。`02_insert_sample.sql` 已内置重复执行检测，会自动清空已有数据。

### 5. 启动应用

```bash
python run.py
```

浏览器访问 **http://127.0.0.1:5000**

> Windows 用户可直接双击 `start.bat` 一键启动。

---

## 测试账号

所有账号的密码统一为 **`123456`**。

| 用户名 | 角色 | 姓名 | 推荐体验路径 |
|--------|------|------|-------------|
| `zhangsan` | 顾客 | 张三 | 浏览商家 → 下单 → 查看订单状态 → 评价 |
| `merchant01` | 商家 | 赵老板 | 管理店铺信息 → 编辑菜品 → 处理新订单 |
| `rider01` | 骑手 | 孙骑手 | 查看待接订单 → 接单 → 取餐 → 送达 |

示例数据包含 **10 个用户**：4 位顾客、3 位商家、3 位骑手。

---

## 技术栈

| 层 | 技术 | 版本 |
|----|------|------|
| 数据库 | SQL Server | — |
| 数据库驱动 | pyodbc + ODBC Driver 17 | ≥ 5.0 |
| ORM | SQLAlchemy | 2.x |
| Web 框架 | Flask | 3.x |
| 模板引擎 | Jinja2 | (随 Flask) |
| 前端 | Bootstrap 5 + Bootstrap Icons | 5.x |
| 表单处理 | WTForms + Flask-WTF | ≥ 1.2 |
| 密码哈希 | Werkzeug (scrypt) | ≥ 3.0 |

---

## 架构设计

### 分层架构

```
HTTP 请求
    │
    ▼
Blueprint (路由层)     ←── 解析请求、参数校验、调用领域层、渲染响应
    │
    ▼
Domain (领域层)        ←── 核心业务逻辑，与 Flask 解耦，可独立测试
    │
    ▼
Models (数据层)        ←── 7 张表的 SQLAlchemy ORM 映射
    │
    ▼
SQL Server
```

- **Routes** — 薄层，只做 HTTP 适配。不包含业务逻辑。
- **Domain** — 封装核心逻辑（订单状态机、鉴权），与 Web 框架解耦，可脱离 HTTP 进行单元测试。
- **Models** — SQLAlchemy ORM 实体，含约束、索引、关系映射。

### 订单状态机

订单状态流转集中在 `app/domain/order_state.py`，一个统一接口覆盖全部 **8 种状态** 的转换校验：

```
                    ┌──────────┐
                    │  pending │  待处理
                    └────┬─────┘
               ┌─────────┼─────────┐
               ▼         ▼         │
          confirmed   cancelled    │
          已确认       已取消       │
               │                   │
               ▼                   │
          preparing                │
          备餐中                    │
               │                   │
               ▼                   │
            ready                  │
           待取餐                   │
               │                   │
          (骑手接单)                │
               ▼                   │
           assigned                │
           配送中                   │
               │                   │
          (骑手取餐)                │
               ▼                   │
           picked_up               │
           已取餐                   │
               │                   │
          (骑手送达)                │
               ▼                   │
           delivered  ◄────────────┘
           已送达
```

**7 种操作**：`confirm`、`prepare`、`ready`、`assign`、`pickup`、`deliver`、`cancel`，每种操作都有角色守卫、状态守卫和资源所有权三重校验。

### 鉴权体系

统一鉴权装饰器 `@require()` 位于 `app/domain/auth.py`，一次声明即完成三层检查：

```python
@require(role='merchant', owns='restaurant')
def edit_restaurant(id):
    ...
```

| 检查层 | 说明 |
|--------|------|
| 登录检查 | 未登录 → 重定向到登录页 |
| 角色校验 | 角色不匹配 → 拒绝访问 |
| 资源所有权 | 商家只能操作自己的店铺；顾客只能取消自己的订单；骑手只能操作自己接的单 |

这一设计替代了散落在各路由文件中的 `@login_required` + `@role_required` + 行内 ownership 查询的碎片化模式。

---

## 数据库设计

### E-R 关系概览

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

### 数据表一览

| 表 | 说明 | 关键约束 |
|----|------|----------|
| `Users` | 用户（顾客 / 商家 / 骑手） | `role IN ('customer','merchant','rider')` |
| `Restaurants` | 商家店铺 | `status IN ('open','closed')`，级联删除 |
| `MenuCategories` | 菜品分类 | 外键到 Restaurants，支持排序 |
| `MenuItems` | 菜品 | `price >= 0`，`status IN ('available','unavailable')` |
| `Orders` | 订单（含配送字段） | 8 种状态约束，含 rider_id/pickup_time/delivery_time |
| `OrderItems` | 订单明细 | `quantity > 0`，快照下单时单价 |
| `Reviews` | 评价 | `rating BETWEEN 1 AND 5`，一个订单一条评价 |

> **v2 架构说明**：原独立的 Delivery（配送）表已合并到 Orders 表中，`rider_id`、`pickup_time`、`delivery_time` 现在直接是 Orders 表的字段。Reviews 表不再冗余存储 `restaurant_id`，通过 `Orders.restaurant_id` 关联查询。

---

## 项目结构

```
takeout/
├── sql/
│   ├── 01_create_tables.sql       # 建库建表脚本（含状态查找表初始数据）
│   └── 02_insert_sample.sql       # 示例数据脚本（可重复执行）
│
├── app/
│   ├── __init__.py                # Flask 工厂函数 (create_app)
│   ├── config.py                  # 数据库与密钥配置（含配送费 DELIVERY_FEE）
│   ├── forms.py                   # WTForms 表单定义（7 个表单类）
│   │
│   ├── domain/                    # 领域逻辑层（与 Flask 解耦）
│   │   ├── __init__.py            # 导出 OrderState, require
│   │   ├── order_state.py         # 订单状态机（核心深度模块）
│   │   └── auth.py                # 统一鉴权装饰器 @require()
│   │
│   ├── models/                    # 数据持久层
│   │   ├── __init__.py            # 模型导出
│   │   └── models.py              # 7 个 SQLAlchemy ORM 实体
│   │
│   ├── routes/                    # HTTP 路由层（薄层）
│   │   ├── auth.py                # 注册 / 登录 / 登出
│   │   ├── restaurant.py          # 商家管理（含分类管理）
│   │   ├── menu.py                # 菜品 CRUD / 上下架
│   │   ├── order.py               # 订单管理（创建、状态流转、评价）
│   │   └── delivery.py            # 配送管理（接单、取餐、送达）
│   │
│   ├── templates/                 # Jinja2 模板（17 个）
│   │   ├── auth/                  # login.html, register.html
│   │   ├── restaurant/            # list, detail, my, create, edit, category_form
│   │   ├── menu/                  # form.html
│   │   ├── order/                 # create, list, detail, review
│   │   ├── delivery/              # available, my
│   │   ├── base.html              # 基础布局（导航栏 + 页脚）
│   │   └── index.html             # 首页
│   │
│   └── static/
│       └── style.css              # 自定义样式
│
├── docs/
│   ├── 系统设计文档.md / .pdf      # 完整系统设计（Mermaid 图表 + 表结构）
│   ├── 软件功能总体设计.md / .pdf   # 软件功能总体设计
│   ├── 01_create_tables详解.md    # 建表脚本详细说明
│   └── agents/                    # Claude Code Agent 配置指引
│
├── CLAUDE.md                      # Claude Code 项目指令
├── PRODUCT.md                     # 产品定义与设计原则
├── requirements.txt               # Python 依赖清单
├── run.py                         # 应用启动入口
└── start.bat                      # Windows 一键启动脚本
```

---

## 设计理念

本项目遵循 `PRODUCT.md` 中定义的设计原则：

1. **功能优先** — 每个元素服务于任务完成，无纯装饰
2. **清晰直白** — 信息层级让下一步操作不言自明
3. **一致可靠** — 三种角色下交互模式统一，状态标签全局一致
4. **轻量克制** — Bootstrap 5 为基础，自定义 CSS 只补不足，不引入前端构建工具

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [系统设计文档](docs/系统设计文档.md) | Mermaid 图表：功能结构图、E-R 图、状态流转图、全部表结构 |
| [软件功能总体设计](docs/软件功能总体设计.md) | 软件功能总体设计方案 |
| [建表脚本详解](docs/01_create_tables详解.md) | SQL 建表脚本逐段说明 |
| [PRODUCT.md](PRODUCT.md) | 产品定义、用户角色、设计原则 |
| [CLAUDE.md](CLAUDE.md) | Claude Code 项目配置与 Agent 指引 |
