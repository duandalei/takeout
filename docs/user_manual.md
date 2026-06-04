# 外卖管理系统 — 用户使用手册

## 1. 环境准备

### 1.1 前置条件

- Windows 系统，已安装 SQL Server（Express 或以上版本）
- Anaconda，已创建 `takeout` 环境
- ODBC Driver 17 for SQL Server

### 1.2 安装依赖

```bash
conda activate takeout
cd C:\Users\段大磊\Desktop\takeout
pip install -r requirements.txt
```

### 1.3 数据库配置

1. 在 SSMS 中创建数据库 `TakeoutDB`
2. 执行建表脚本：打开 `sql/01_create_tables.sql` 并运行
3. 执行示例数据：打开 `sql/02_insert_sample.sql` 并运行

### 1.4 修改连接配置

编辑 `app/config.py`，修改数据库连接参数：

```python
DB_SERVER   = 'localhost'   # 你的 SQL Server 地址
DB_PORT     = '1433'        # 端口
DB_NAME     = 'TakeoutDB'   # 数据库名
DB_USER     = 'sa'          # 用户名
DB_PASSWORD = '123456'      # 密码
```

## 2. 启动系统

```bash
conda activate takeout
cd C:\Users\段大磊\Desktop\takeout
python run.py
```

浏览器访问：**http://127.0.0.1:5000**

## 3. 功能指南

### 3.1 注册 & 登录

1. 点击右上角「注册」
2. 选择角色：顾客、商家、骑手
3. 填写基本信息并提交
4. 注册成功后跳转到登录页
5. 输入用户名密码登录

### 3.2 顾客操作

#### 浏览商家 & 下单
1. 点击导航栏「商家浏览」
2. 查看营业中的商家列表
3. 点击「查看菜单」进入商家详情
4. 点击「去下单」
5. 选择菜品和数量（点击 +/- 按钮）
6. 填写配送地址和备注
7. 点击「提交订单」

#### 查看订单
1. 点击导航栏「我的订单」
2. 可查看所有订单的状态
3. 点击「查看详情」了解订单进度

#### 取消订单
- 在订单详情页，panding/confirmed 状态的订单可点击「取消订单」

#### 评价
- delivered 状态的订单，在详情页会出现「评价」按钮
- 选择评分 1-5 星，填写评价内容

### 3.3 商家操作

#### 创建店铺
1. 注册时选择角色「商家」
2. 登录后点击「我的店铺」
3. 如未创建店铺，会引导创建
4. 填写店铺名称、地址、电话、描述

#### 管理菜品
1. 在「我的店铺」页面，点击「添加分类」
2. 创建分类后，点击「添加菜品」
3. 填写菜品名称、价格、选择分类
4. 可编辑、上架/下架、删除菜品

#### 处理订单
1. 点击「查看本店订单」
2. 对 pending 状态的订单点击「接单」
3. 订单依次流转：confirmed → preparing → delivering
4. preparing 状态时点击「备好待取」→ 等待骑手取餐

### 3.4 骑手操作

#### 接单
1. 注册时选择角色「骑手」
2. 登录后点击「待接配送」
3. 查看待配送订单列表
4. 点击「接单」按钮接单
5. 接单后记录出现在「我的配送」

#### 配送流程
1. 到店取餐后 → 在「我的配送」中点击「确认取餐」
2. 送达后 → 点击「确认送达」
3. 配送完成

### 3.5 管理员操作

管理员拥有所有页面访问权限，可在管理面板中查看系统数据。

## 4. 订单状态说明

| 状态 | 含义 | 操作者 |
|------|------|--------|
| pending | 待接单 | 顾客已下单，等待商家确认 |
| confirmed | 已接单 | 商家已确认，准备备餐 |
| preparing | 备餐中 | 商家正在准备餐品 |
| delivering | 配送中 | 餐备好，骑手可取餐/配送 |
| delivered | 已送达 | 订单完成 |
| cancelled | 已取消 | 顾客或商家取消 |

## 5. 常见问题

**Q: 无法连接数据库？**
- 检查 SQL Server 是否运行（SQL Server Configuration Manager）
- 确认 TCP/IP 已启用，端口 1433
- 检查 `config.py` 中的连接信息

**Q: ODBC Driver 17 未安装？**
- 下载安装：[Microsoft ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

**Q: 模板报错或样式异常？**
- 确保能访问 Bootstrap CDN（联网环境）
- 或下载 Bootstrap 到 `app/static/` 本地引用
