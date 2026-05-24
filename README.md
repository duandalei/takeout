# 外卖点餐系统

数据库课程设计项目，基于 **SQL Server + Flask + Vue 3** 实现外卖点餐核心业务流程。

## 技术栈

| 层 | 技术 | 说明 |
|---|------|------|
| 数据库 | SQL Server 2019+ | Windows 认证，数据库名 `TakeoutDB` |
| 后端 | Python 3 + Flask | pyodbc 直连数据库，无 ORM |
| 前端 | Vue 3 + Vite + Vue Router + Axios | SPA，Hash 路由 |
| 环境 | Anaconda (`takeout` env) | 见 `python环境来源说明.txt` |

---

## 项目结构

```
外卖点餐系统/
├── database/
│   └── init.sql                  # 建库脚本：9 张表 + 索引 + 种子数据
├── backend/                      # Flask 后端 (端口 5000)
│   ├── app.py                    # 应用入口：create_app() 注册 7 个 Blueprint
│   ├── config.py                 # DB_CONFIG 字典 + SECRET_KEY
│   ├── requirements.txt          # flask, flask-cors, pyodbc
│   ├── models/                   # 数据访问层 (每个文件一个业务域)
│   │   ├── db.py                 #   底层：get_connection / query / execute
│   │   ├── user.py               #   用户：find_by_phone / find_by_id / create
│   │   ├── merchant.py           #   商家：list_all / find_by_id / get_menu
│   │   ├── dish.py               #   菜品：find_by_id
│   │   ├── address.py            #   地址：CRUD
│   │   ├── order.py              #   订单：create(事务) / find_by_id / list_by_* / assign_rider
│   │   ├── rider.py              #   骑手：find_free_rider / get_available_orders / set_status
│   │   └── review.py             #   评价：create(自动更新商家评分) / get_by_order
│   └── routes/                   # REST API 路由 (每个文件一个 Blueprint)
│       ├── auth.py               #   /api/auth/*       认证 + token 管理
│       ├── merchants.py          #   /api/merchants/*  商家列表 + 菜单
│       ├── dishes.py             #   /api/dishes/*     菜品详情
│       ├── addresses.py          #   /api/addresses/*  地址 CRUD
│       ├── orders.py             #   /api/orders/*     下单/支付/取消 + 商家接单
│       ├── riders.py             #   /api/rider/*      骑手接单/送达/可接订单
│       └── reviews.py            #   /api/reviews/*    评价
├── frontend/                     # Vue 3 前端 (端口 3000)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js            #   代理 /api → localhost:5000
│   ├── dist/                     #   构建产物
│   └── src/
│       ├── main.js               #   入口：createApp + router
│       ├── App.vue               #   根组件：顶栏导航 + <router-view>
│       ├── api/index.js          #   Axios 实例 + 拦截器 + 所有 API 函数
│       ├── router/index.js       #   路由表 + 导航守卫 (登录/角色校验)
│       └── views/                #   页面组件 (按角色分类)
│           ├── Login.vue         #     登录/注册
│           ├── Home.vue          #     顾客：商家列表
│           ├── Merchant.vue      #     顾客：商家详情 + 菜单 + 购物车浮层
│           ├── Cart.vue          #     顾客：结算页
│           ├── Orders.vue        #     顾客：订单列表
│           ├── OrderDetail.vue   #     顾客：订单详情 + 支付/取消/评价
│           ├── Addresses.vue     #     顾客：地址管理
│           ├── Rider.vue         #     骑手：可接订单 + 我的配送
│           └── MerchantDashboard.vue  # 商家：订单管理
```

---

## 数据库设计

### 表关系 ER 图

```
users ──1:N── orders ──1:N── order_items ──N:1── dishes
  │              │                                   │
  │              └──N:1── merchants ──1:N── categories
  │              │                │
  │              └──N:1── addresses
  │              │
  │              └──N:1── riders
  │
  └──1:N── reviews ──N:1── merchants
```

### 9 张表详解

| 表 | 主键 | 核心字段 | 说明 |
|----|------|---------|------|
| `users` | user_id (IDENTITY) | phone, password_hash, nickname, role | role: customer/rider/merchant |
| `merchants` | merchant_id | user_id, name, rating, monthly_sales, min_delivery_price, delivery_fee, status | status: 1=营业 0=休息 |
| `categories` | category_id | merchant_id, name, sort_order | 商家自定义菜品分类 |
| `dishes` | dish_id | merchant_id, category_id, name, price, monthly_sales, status | status: 1=上架 0=下架 |
| `addresses` | address_id | user_id, contact_name, phone, province/city/district, detail, is_default | 用户配送地址 |
| `riders` | rider_id | user_id, name, phone, status | status: 1=空闲 2=配送中 0=离线 |
| `orders` | order_id (BIGINT) | user_id, merchant_id, address_id, rider_id, total_price, delivery_fee, actual_amount, status, remark, paid_at, delivered_at | 核心表，见下方状态流转 |
| `order_items` | item_id | order_id, dish_id, dish_name, dish_price, quantity | dish_name/price 是下单时的快照 |
| `reviews` | review_id | order_id (UNIQUE), user_id, merchant_id, rating (1-5), content | 一个订单一条评价 |

### 订单状态流转

```
  用户下单
    │
    ▼
┌─────────┐    用户支付    ┌─────────┐   骑手接单    ┌─────────┐   骑手送达    ┌─────────┐
│ 1 待支付 │ ──────────→ │ 2 待接单 │ ──────────→ │ 3 配送中 │ ──────────→ │ 4 已送达 │
└─────────┘              └─────────┘              └─────────┘              └─────────┘
    │                        │                        │
    │     用户取消            │     用户取消            │     (不可取消)
    └──────────────────────→ └──────────────────────→
                                  │
                                  ▼
                            ┌─────────┐
                            │ 5 已取消 │
                            └─────────┘
```

关键规则：
- **支付** (1→2)：记录 `paid_at` 时间戳
- **商家接单**：仅确认订单有效性，不分配骑手，状态保持 2
- **骑手接单** (2→3)：设置 `rider_id`，骑手状态改为 2 (配送中)
- **骑手送达** (3→4)：记录 `delivered_at`，若骑手无其他配送订单则恢复空闲 (status=1)
- **取消** (1/2→5)：仅在待支付或待接单时可取消
- **评价**：仅已送达 (status=4) 且未评价的订单，提交后自动更新商家评分 (AVG)

### 索引策略

```sql
users(phone)                        -- 手机号登录查询
orders(user_id, created_at DESC)    -- 用户订单列表 (按时间倒序)
orders(merchant_id, status)         -- 商家按状态筛选订单
orders(rider_id, status)            -- 骑手按状态筛选订单
dishes(merchant_id, category_id)    -- 商家菜单查询
order_items(order_id)               -- 订单明细关联
reviews(merchant_id)                -- 商家评价查询 + 评分更新
```

---

## 后端架构

### 1. 应用入口 (`app.py`)

Flask 应用工厂模式 `create_app()`：注册 7 个 Blueprint，启用 CORS，设置 `JSON_AS_ASCII = False` 支持中文输出。

### 2. 数据库连接 (`models/db.py`)

pyodbc + Windows 认证直连 SQL Server，提供三个函数：

| 函数 | 返回 | 用途 |
|------|------|------|
| `query(sql, params)` | `list[dict]` | SELECT 查询，自动转字典列表 |
| `execute(sql, params)` | `int` (last insert id) | INSERT/UPDATE/DELETE，自动 commit |
| `get_connection()` | `pyodbc.Connection` | 用于需手动控制事务的场景 (如下单) |

连接字符串格式：`DRIVER={ODBC Driver 17}; SERVER=localhost; DATABASE=TakeoutDB; Trusted_Connection=yes`

### 3. 认证机制 (`routes/auth.py`)

- **密码**：前端明文传输，后端 SHA256 哈希后存储
- **Token**：`secrets.token_hex(32)` 生成 64 字符随机串，存入内存 `tokens` 字典
- **Token 映射**：`{token: {"user_id": int, "role": str}}` — 服务重启全部失效
- **请求鉴权**：`Authorization: Bearer <token>` 头 → `get_user_id_from_token()` 解析
- **角色鉴权**：`require_role(*roles)` 同时校验登录状态和角色，返回 `(user_id, error)`

### 4. 下单事务 (`models/order.py`)

```python
def create(user_id, merchant_id, address_id, ...):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders ...")      # 1. 插入订单
        cursor.execute("SELECT @@IDENTITY")           # 2. 获取 order_id
        for item in items:
            cursor.execute("INSERT INTO order_items ...")  # 3. 逐条插入明细
        conn.commit()                                 # 4. 统一提交
```

使用显式事务保证订单和明细的原子性。

### 5. 完整 API 列表

#### 认证 (`auth_bp`)
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/auth/register` | 否 | body: `{phone, password, nickname, role}` |
| POST | `/api/auth/login` | 否 | body: `{phone, password}` → 返回 token |
| GET | `/api/auth/me` | 是 | 返回当前登录用户信息 |

#### 商家 (`merchants_bp`)
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/merchants` | 否 | 所有营业中的商家，按月销量降序 |
| GET | `/api/merchants/<id>` | 否 | 商家详情 + 按分类组织的菜单 |
| GET | `/api/merchants/<id>/menu` | 否 | 仅菜单 (分类→菜品列表) |

#### 菜品 (`dishes_bp`)
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/dishes/<id>` | 否 | 单个菜品详情 |

#### 地址 (`addresses_bp`)
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/addresses` | 是 | 当前用户的地址列表 |
| POST | `/api/addresses` | 是 | body: `{contact_name, phone, province, city, district, detail}` |
| PUT | `/api/addresses/<id>` | 是 | 仅限地址所有者 |
| DELETE | `/api/addresses/<id>` | 是 | 仅限地址所有者 |

#### 订单 (`orders_bp`)
| 方法 | 路径 | 认证 | 角色 | 说明 |
|------|------|------|------|------|
| POST | `/api/orders` | 是 | customer | 下单 (事务)，body: `{merchant_id, address_id, items, remark}` |
| GET | `/api/orders` | 是 | 任意 | 当前用户的订单列表 |
| GET | `/api/orders/<id>` | 是 | 任意 | 订单详情 (含 items + review) |
| PUT | `/api/orders/<id>/pay` | 是 | customer | 支付 (1→2)，记录 paid_at |
| PUT | `/api/orders/<id>/cancel` | 是 | customer | 取消 (1/2→5) |
| GET | `/api/merchant/orders` | 是 | merchant | 本店订单列表，可选 `?status=` 过滤 |
| PUT | `/api/merchant/orders/<id>/accept` | 是 | merchant | 商家确认订单 (仅校验，不分配骑手) |

#### 骑手 (`riders_bp`)
| 方法 | 路径 | 认证 | 角色 | 说明 |
|------|------|------|------|------|
| GET | `/api/rider/available` | 是 | rider | 所有可接订单 (status=2, rider_id IS NULL) |
| GET | `/api/rider/orders` | 是 | rider | 当前骑手的配送订单 (status=3/4) |
| PUT | `/api/rider/orders/<id>/accept` | 是 | rider | 骑手接单 (2→3)，设置 rider_id，骑手→忙碌 |
| PUT | `/api/rider/orders/<id>/deliver` | 是 | rider | 确认送达 (3→4)，无剩余配送则骑手→空闲 |
| GET | `/api/riders` | 否 | 任意 | 所有空闲骑手列表 (status=1) |

#### 评价 (`reviews_bp`)
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/reviews` | 是 | body: `{order_id, rating, content}`，自动重算商家评分 |
| GET | `/api/reviews/merchant/<id>` | 否 | 商家评价列表 (含用户昵称) |

---

## 前端架构

### 1. 路由设计

使用 `createWebHashHistory` (Hash 模式，`#/path`)，9 条路由：

| 路径 | 页面 | meta.role | 说明 |
|------|------|-----------|------|
| `/` | → 重定向 `/home` | - | 默认跳转 |
| `/login` | Login.vue | - | 登录/注册，已登录用户自动跳转角色首页 |
| `/home` | Home.vue | - | 商家列表 |
| `/merchant/:id` | Merchant.vue | - | 商家菜单 + 购物车 |
| `/cart` | Cart.vue | - | 结算下单 |
| `/orders` | Orders.vue | - | 我的订单 |
| `/order/:id` | OrderDetail.vue | - | 订单详情 (支付/取消/评价) |
| `/addresses` | Addresses.vue | - | 地址管理 |
| `/rider` | Rider.vue | `role: "rider"` | 骑手面板 (可接单 + 我的配送) |
| `/merchant/dashboard` | MerchantDashboard.vue | `role: "merchant"` | 商家订单管理 |

### 2. 导航守卫 (`router/index.js`)

```
未登录 + 非 /login → 重定向 /login
已登录 + 访问 /login → 按角色跳转首页
路由有 meta.role + 用户角色不匹配 → 重定向 /home
```

### 3. 状态管理

不使用 Vuex/Pinia，全部通过 `localStorage` 管理：

| 键 | 内容 | 读写位置 |
|----|------|---------|
| `token` | 认证 token 字符串 | Login.vue 写入，api/index.js 拦截器读取 |
| `user` | `JSON.stringify({user_id, nickname, role})` | Login.vue / App.vue 写入，导航栏/路由守卫读取 |
| `takeout_cart` | `JSON.stringify([{dish_id, name, price, quantity, merchant_id, merchant_name}])` | Merchant.vue 写入，Cart.vue 读取并清空 |

### 4. Axios 封装 (`api/index.js`)

- `baseURL: "/api"` → Vite proxy 转发到 `localhost:5000`
- **请求拦截器**：自动附加 `Authorization: Bearer <token>`
- **响应拦截器**：401 时清除 token 并重定向 `/login`
- 导出所有后端 API 对应的函数

### 5. 页面组件职责

#### 顾客端 (6 页)

| 页面 | 核心逻辑 |
|------|---------|
| **Home.vue** | `onMounted` 加载商家列表 → 卡片展示 (评分/月售/起送价/配送费) → 点击进入商家 |
| **Merchant.vue** | 加载商家菜单 (分类 Tab + 菜品列表) → 每个菜品 +/- 按钮修改 localStorage 购物车 → 底部浮层显示总价和数量 → 点击去结算 |
| **Cart.vue** | 从 localStorage 读购物车 → 选择地址 (API 加载) → 显示价格明细 → 校验起送价 → POST 创建订单 → 清空购物车 → 跳转订单详情 |
| **Orders.vue** | 加载用户订单列表 → 状态 Badge + 金额 + 时间 → 点击进入详情 |
| **OrderDetail.vue** | 加载订单详情 (状态/时间/菜品/金额/评价) → 按状态显示操作按钮：支付(1)/取消(1-2)/评价(4 未评) |
| **Addresses.vue** | 地址 CRUD，含省市区表单 |

#### 骑手端 (1 页)

| 页面 | 核心逻辑 |
|------|---------|
| **Rider.vue** | 双区域布局 → 上：**可接订单** (API: `/rider/available`, 所有 status=2 无人接单的订单) 带"接单"按钮 → 下：**我的配送** (API: `/rider/orders`, status=3 可点"确认送达", status=4 显示已送达) → 接单/送达后自动刷新 |

#### 商家端 (1 页)

| 页面 | 核心逻辑 |
|------|---------|
| **MerchantDashboard.vue** | 状态筛选 Tab (全部/待接单/配送中/已送达) → 订单卡片 (客户/地址/金额) → 待接单(status=2)显示"接单"确认按钮 |

---

## 启动步骤

### 1. 数据库

在 SQL Server Management Studio 中打开并执行 `database/init.sql`，脚本会：
- 创建数据库 `TakeoutDB` (如不存在)
- 建 9 张表 (先 DROP 后 CREATE)
- 创建 7 个索引
- 插入种子数据：4 个用户 (密码 `123456`) + 2 个商家 + 7 个菜品 + 1 个地址 + 2 个骑手

### 2. 后端

```bash
cd backend
conda activate takeout
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 4. 测试账号

| 角色 | 手机号 | 密码 |
|------|--------|------|
| 顾客 (张三) | 13800000001 | 123456 |
| 顾客 (李四) | 13800000002 | 123456 |
| 骑手 (王骑手) | 13900000001 | 123456 |
| 骑手 (赵骑手) | 13900000002 | 123456 |
| 商家 (黄焖鸡) | 13800000010 | 123456 |
| 商家 (奶茶店) | 13800000020 | 123456 |

### 5. 完整业务流程

```
顾客登录 → 浏览商家 → 选择菜品加入购物车 → 去结算(选地址/确认金额)
  → 下单(status=1) → 立即支付(status=2)
  → 商家登录 → 确认订单
  → 骑手登录 → 在"可接订单"中看到该单 → 点击接单(status=3)
  → 骑手配送 → 确认送达(status=4)
  → 顾客在订单详情中看到"已送达" → 去评价
  → 评价提交后商家评分自动更新
```

---

## 关键技术决策

1. **无 ORM**：使用 pyodbc 原生 SQL，`models/db.py` 仅 48 行封装，适合课程设计理解数据库原理
2. **Token 存内存**：没有使用 JWT 或 Redis，服务重启丢失所有登录态，适合开发调试
3. **Hash 路由**：`createWebHashHistory` 避免后端 URL 重写配置
4. **购物车存 localStorage**：不持久化到服务端，简化状态管理
5. **菜品快照**：`order_items` 存储下单时的 `dish_name` 和 `dish_price`，后续菜品调价不影响历史订单
6. **商家评分自动更新**：评价提交后触发 `AVG(rating)` 更新 `merchants.rating`
7. **骑手自主接单**：与"系统自动派单"模式不同，骑手在可接订单池中自主选择
