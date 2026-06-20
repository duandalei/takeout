## 总ER图

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px', 'primaryColor': '#4A90D9', 'primaryTextColor': '#fff', 'lineColor': '#555', 'fontFamily': 'Microsoft YaHei, sans-serif'}}}%%
flowchart LR
    %% ===== 实体 =====
    U["Users<br/>用户"]
    R["Restaurants<br/>商家"]
    MC["MenuCategories<br/>菜品分类"]
    MI["MenuItems<br/>菜品"]
    O["Orders<br/>订单"]
    OI["OrderItems<br/>订单明细"]
    Rev["Reviews<br/>评价"]

    %% ===== 联系 =====
    Rel1{"拥有<br/>1:N"}
    Rel2{"包含<br/>1:N"}
    Rel3{"包含<br/>1:N"}
    Rel4{"下单<br/>1:N"}
    Rel5{"包含<br/>1:N"}
    Rel6{"对应<br/>N:1"}
    Rel7{"对应<br/>1:1"}
    Rel8{"来自<br/>N:1"}
    Rel9{"配送<br/>N:1"}

    %% ===== 连线 =====
    U -- "1" --> Rel1
    Rel1 -- "N" --> R

    R -- "1" --> Rel2
    Rel2 -- "N" --> MC

    MC -- "1" --> Rel3
    Rel3 -- "N" --> MI

    U -- "1" --> Rel4
    Rel4 -- "N" --> O

    O -- "1" --> Rel5
    Rel5 -- "N" --> OI

    OI -- "N" --> Rel6
    Rel6 -- "1" --> MI

    O -- "1" --> Rel7
    Rel7 -- "1" --> Rev

    Rev -- "N" --> Rel8
    Rel8 -- "1" --> U

    O -- "N" --> Rel9
    Rel9 -- "1" --> U
```

该 E-R 模型完整描述外卖配送系统中各实体间的关联关系，涵盖用户、商家、菜品分类、菜品、订单、订单明细、评价共 7 个实体。其中用户与商家之间存在一对多联系"拥有"；用户与订单之间存在一对多联系"下单"（顾客角色）和"配送"（骑手角色）；商家与菜品分类、菜品之间存在一对多联系"包含"；菜品分类与菜品之间存在一对多联系"归类"；订单与订单明细之间存在一对多联系"包含明细"；菜品与订单明细之间存在多对一联系"对应菜品"；订单与评价之间存在一对一联系"获得评价"；用户与评价之间存在一对多联系"发表评价"。该模型为后续逻辑结构设计与数据库实现提供清晰的概念框架。


# 用户实体属性 E-R 图

实体为用户，属性包括：用户ID、用户名、密码哈希、真实姓名、电话、地址、角色。其中用户ID为主键，用户名为唯一键。角色字段限定为顾客、商家、骑手三种取值，新用户注册时自主选择身份，系统基于角色实现权限分级控制。

```mermaid
graph LR
    User((用户)) --- PK([用户ID PK])
    User --- A1([用户名 UK])
    User --- A2[密码哈希]
    User --- A3[真实姓名]
    User --- A4[电话]
    User --- A5[地址]
    User --- A6[角色]
```


# 商家实体属性 E-R 图

实体为商家，属性包括：店铺ID、店主ID、店铺名称、地址、电话、描述、营业状态。其中店铺ID为主键，店主ID为外键关联用户表。营业状态在"营业中"与"已歇业"之间切换，歇业店铺对顾客不可见。

```mermaid
graph LR
    Restaurant((商家)) --- PK([店铺ID PK])
    Restaurant --- FK([店主ID FK])
    Restaurant --- A1[店铺名称]
    Restaurant --- A2[地址]
    Restaurant --- A3[电话]
    Restaurant --- A4[描述]
    Restaurant --- A5[营业状态]
```


# 菜品分类实体属性 E-R 图

实体为菜品分类，属性包括：分类ID、店铺ID、分类名称、排序号。其中分类ID为主键，店铺ID为外键关联商家表。排序号用于前端拖拽排序，数值越小展示越靠前。

```mermaid
graph LR
    Category((菜品分类)) --- PK([分类ID PK])
    Category --- FK([店铺ID FK])
    Category --- A1[分类名称]
    Category --- A2[排序号]
```


# 菜品实体属性 E-R 图

实体为菜品，属性包括：菜品ID、店铺ID、分类ID、菜品名称、描述、价格、状态。其中菜品ID为主键，店铺ID和分类ID为外键分别关联商家表和分类表。状态控制菜品上下架，仅上架菜品对顾客可见。

```mermaid
graph LR
    Item((菜品)) --- PK([菜品ID PK])
    Item --- FK1([店铺ID FK])
    Item --- FK2([分类ID FK])
    Item --- A1[菜品名称]
    Item --- A2[描述]
    Item --- A3[价格]
    Item --- A4[状态]
```


# 订单实体属性 E-R 图

实体为订单，属性包括：订单ID、顾客ID、店铺ID、骑手ID、配送地址、订单状态、总金额、配送费、备注、取餐时间、送达时间、创建时间。其中订单ID为主键，顾客ID、店铺ID、骑手ID为外键分别关联用户表和商家表。订单状态随商家和骑手操作依次流转，涵盖待处理、已确认、备餐中、待取餐、配送中、已取餐、已送达、已取消共 8 种状态。

```mermaid
graph LR
    Order((订单)) --- PK([订单ID PK])
    Order --- FK1([顾客ID FK])
    Order --- FK2([店铺ID FK])
    Order --- FK3([骑手ID FK])
    Order --- A1[配送地址]
    Order --- A2[订单状态]
    Order --- A3[总金额]
    Order --- A4[配送费]
    Order --- A5[备注]
    Order --- A6[取餐时间]
    Order --- A7[送达时间]
    Order --- A8[创建时间]
```


# 订单明细实体属性 E-R 图

实体为订单明细，属性包括：明细ID、订单ID、菜品ID、数量、单价。其中明细ID为主键，订单ID和菜品ID为外键分别关联订单表和菜品表。每条明细记录顾客所点的一个菜品及其数量和下单时单价，多条明细汇总构成订单总金额。

```mermaid
graph LR
    OrderItem((订单明细)) --- PK([明细ID PK])
    OrderItem --- FK1([订单ID FK])
    OrderItem --- FK2([菜品ID FK])
    OrderItem --- A1[数量]
    OrderItem --- A2[单价]
```


# 评价实体属性 E-R 图

实体为评价，属性包括：评价ID、订单ID、顾客ID、评分、评论内容、创建时间。其中评价ID为主键，订单ID为唯一外键（一个订单仅对应一条评价），顾客ID为外键关联用户表。评分限定 1-5 星，仅已送达订单可评价。

```mermaid
graph LR
    Review((评价)) --- PK([评价ID PK])
    Review --- FK1([订单ID UK])
    Review --- FK2([顾客ID FK])
    Review --- A1[评分]
    Review --- A2[评论内容]
    Review --- A3[创建时间]
```