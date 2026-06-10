"""SQLAlchemy data models — 7 entities across 7 tables (was 8, Delivery collapsed into Orders)."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Index

db = SQLAlchemy()


# ============================================================
# 0. 订单状态查找表
# ============================================================
class OrderStatus(db.Model):
    __tablename__ = 'OrderStatuses'

    status_code  = db.Column(db.String(20), primary_key=True)
    display_name = db.Column(db.String(50), nullable=False)
    sequence     = db.Column(db.Integer, nullable=False)
    is_terminal  = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<OrderStatus {self.status_code}: {self.display_name}>'


# ============================================================
# 1. 用户表
# ============================================================
class User(db.Model):
    __tablename__ = 'Users'

    user_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username     = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name    = db.Column(db.String(50), nullable=False)
    phone        = db.Column(db.String(20), nullable=False)
    email        = db.Column(db.String(100))
    address      = db.Column(db.String(200))
    role         = db.Column(db.String(20), nullable=False, default='customer')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "role IN ('customer','merchant','rider')",
            name='CK_Users_Role',
        ),
        Index('IX_Users_Role', 'role'),
    )

    # relationships
    restaurants      = db.relationship('Restaurant', backref='owner',     lazy='dynamic')
    orders_customer  = db.relationship('Order', foreign_keys='Order.customer_id', backref='customer', lazy='dynamic')
    orders_rider     = db.relationship('Order', foreign_keys='Order.rider_id',    backref='rider',    lazy='dynamic')
    reviews          = db.relationship('Review',    backref='customer_info', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.user_id}: {self.username} ({self.role})>'


# ============================================================
# 2. 商家表
# ============================================================
class Restaurant(db.Model):
    __tablename__ = 'Restaurants'

    restaurant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id      = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete='CASCADE'), nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    address       = db.Column(db.String(200), nullable=False)
    phone         = db.Column(db.String(20), nullable=False)
    description   = db.Column(db.String(500))
    logo_url      = db.Column(db.String(255))
    status        = db.Column(db.String(20), nullable=False, default='open')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("status IN ('open','closed')", name='CK_Restaurants_Status'),
        Index('IX_Restaurants_Status', 'status'),
        Index('IX_Restaurants_Owner', 'owner_id'),
    )

    categories    = db.relationship('MenuCategory', backref='restaurant', lazy='dynamic',
                                    cascade='all, delete-orphan')
    menu_items    = db.relationship('MenuItem', backref='restaurant', lazy='dynamic')
    orders        = db.relationship('Order', backref='restaurant', lazy='dynamic')

    def __repr__(self):
        return f'<Restaurant {self.restaurant_id}: {self.name}>'


# ============================================================
# 3. 菜品分类表
# ============================================================
class MenuCategory(db.Model):
    __tablename__ = 'MenuCategories'

    category_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('Restaurants.restaurant_id', ondelete='CASCADE'), nullable=False)
    name          = db.Column(db.String(50), nullable=False)
    sort_order    = db.Column(db.Integer, nullable=False, default=0)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('IX_Categories_Restaurant', 'restaurant_id'),
    )

    items = db.relationship('MenuItem', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<MenuCategory {self.category_id}: {self.name}>'


# ============================================================
# 4. 菜品表
# ============================================================
class MenuItem(db.Model):
    __tablename__ = 'MenuItems'

    item_id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('Restaurants.restaurant_id'), nullable=False)
    category_id   = db.Column(db.Integer, db.ForeignKey('MenuCategories.category_id'), nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.String(500))
    price         = db.Column(db.Numeric(10, 2), nullable=False)
    image_url     = db.Column(db.String(255))
    status        = db.Column(db.String(20), nullable=False, default='available')
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("price >= 0",       name='CK_Items_Price'),
        CheckConstraint("status IN ('available','unavailable')", name='CK_Items_Status'),
        Index('IX_Items_Restaurant', 'restaurant_id'),
        Index('IX_Items_Category', 'category_id'),
        Index('IX_Items_Status', 'status'),
    )

    order_items = db.relationship('OrderItem', backref='menu_item', lazy='dynamic')

    def __repr__(self):
        return f'<MenuItem {self.item_id}: {self.name} ¥{self.price}>'


# ============================================================
# 5. 订单表 (absorbed old Delivery table)
# ============================================================
class Order(db.Model):
    __tablename__ = 'Orders'

    order_id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id      = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    restaurant_id    = db.Column(db.Integer, db.ForeignKey('Restaurants.restaurant_id'), nullable=False)
    rider_id         = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)
    delivery_address = db.Column(db.String(200), nullable=False)
    status           = db.Column(db.String(20), nullable=False, default='pending')
    total_amount     = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    delivery_fee     = db.Column(db.Numeric(10, 2), nullable=False, default=5.00)
    note             = db.Column(db.String(500))
    # Delivery fields (was a separate table)
    pickup_time      = db.Column(db.DateTime, nullable=True)
    delivery_time    = db.Column(db.DateTime, nullable=True)
    # Timestamps
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("total_amount >= 0", name='CK_Orders_Amount'),
        CheckConstraint("delivery_fee >= 0", name='CK_Orders_DeliveryFee'),
        CheckConstraint(
            "status IN ("
            "'pending','confirmed','preparing','ready',"
            "'assigned','picked_up','delivered','cancelled'"
            ")",
            name='CK_Orders_Status',
        ),
        Index('IX_Orders_Customer', 'customer_id'),
        Index('IX_Orders_Restaurant', 'restaurant_id'),
        Index('IX_Orders_Rider', 'rider_id'),
        Index('IX_Orders_Status', 'status'),
    )

    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic',
                                   cascade='all, delete-orphan')
    review      = db.relationship('Review', backref='order', uselist=False,
                                   cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.order_id}: status={self.status} amount={self.total_amount}>'


# ============================================================
# 6. 订单明细表
# ============================================================
class OrderItem(db.Model):
    __tablename__ = 'OrderItems'

    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id      = db.Column(db.Integer, db.ForeignKey('Orders.order_id', ondelete='CASCADE'), nullable=False)
    item_id       = db.Column(db.Integer, db.ForeignKey('MenuItems.item_id'), nullable=False)
    quantity      = db.Column(db.Integer, nullable=False)
    unit_price    = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0",   name='CK_OrderItems_Qty'),
        CheckConstraint("unit_price >= 0", name='CK_OrderItems_Price'),
        Index('IX_OrderItems_Order', 'order_id'),
    )

    def __repr__(self):
        return f'<OrderItem {self.order_item_id}: item={self.item_id} qty={self.quantity}>'


# ============================================================
# 7. 评价表 (restaurant_id removed — queried through Orders)
# ============================================================
class Review(db.Model):
    __tablename__ = 'Reviews'

    review_id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id      = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), unique=True, nullable=False)
    customer_id   = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    rating        = db.Column(db.SmallInteger, nullable=False)
    comment       = db.Column(db.String(500))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name='CK_Reviews_Rating'),
        Index('IX_Reviews_Order', 'order_id'),
    )

    def __repr__(self):
        return f'<Review {self.review_id}: order={self.order_id} rating={self.rating}>'
