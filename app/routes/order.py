"""订单路由: 下单 / 我的订单 / 接单 / 状态流转 / 评价"""

import json
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.models import db, Order, OrderItem, MenuItem, Restaurant, Delivery, Review
from app.forms import OrderForm, ReviewForm
from app.routes.auth import login_required, role_required

order_bp = Blueprint('order', __name__)


# ============================================================
# 从商家详情页下单
# ============================================================
@order_bp.route('/create/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def create(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if restaurant.status != 'open':
        flash('该商家已歇业', 'warning')
        return redirect(url_for('restaurant.list_restaurants'))

    # 获取该商家所有在售菜品
    items = (
        MenuItem.query
        .filter_by(restaurant_id=restaurant_id, status='available')
        .order_by(MenuItem.category_id, MenuItem.name)
        .all()
    )

    form = OrderForm()
    if form.validate_on_submit():
        # 从表单获取购物车数据 (JSON: {item_id: quantity})
        cart_json = request.form.get('cart_data', '{}')
        try:
            cart = json.loads(cart_json)
        except json.JSONDecodeError:
            cart = {}

        if not cart:
            flash('请至少选择一个菜品', 'warning')
            return redirect(url_for('order.create', restaurant_id=restaurant_id))

        # 计算订单总金额并建立订单明细
        total = 0
        order_items = []
        for item_id_str, qty_str in cart.items():
            qty = int(qty_str)
            if qty <= 0:
                continue
            item = MenuItem.query.get(int(item_id_str))
            if not item or item.restaurant_id != restaurant_id:
                continue
            total += item.price * qty
            order_items.append(OrderItem(
                item_id=item.item_id,
                quantity=qty,
                unit_price=item.price,
            ))

        if not order_items:
            flash('购物车为空', 'warning')
            return redirect(url_for('order.create', restaurant_id=restaurant_id))

        order = Order(
            customer_id=session['user_id'],
            restaurant_id=restaurant_id,
            delivery_address=form.delivery_address.data,
            status='pending',
            total_amount=total,
            note=form.note.data or None,
        )
        order.order_items = order_items
        db.session.add(order)
        db.session.commit()

        flash(f'订单已提交！总计 ¥{total:.2f}', 'success')
        return redirect(url_for('order.my_orders'))

    return render_template('order/create.html',
                           restaurant=restaurant,
                           items=items,
                           form=form)


# ============================================================
# 我的订单 (不同角色看到不同内容)
# ============================================================
@order_bp.route('/my')
@login_required
def my_orders():
    user_id = session['user_id']
    role = session['role']

    if role == 'customer':
        orders = (
            Order.query
            .filter_by(customer_id=user_id)
            .order_by(Order.created_at.desc())
            .all()
        )
    elif role == 'merchant':
        restaurant = Restaurant.query.filter_by(owner_id=user_id).first()
        if not restaurant:
            orders = []
        else:
            orders = (
                Order.query
                .filter_by(restaurant_id=restaurant.restaurant_id)
                .order_by(Order.created_at.desc())
                .all()
            )
    else:
        orders = []

    return render_template('order/list.html', orders=orders)


# ============================================================
# 订单详情
# ============================================================
@order_bp.route('/<int:id>')
@login_required
def detail(id):
    order = Order.query.get_or_404(id)
    return render_template('order/detail.html', order=order)


# ============================================================
# 商家接单 / 取消订单
# ============================================================
@order_bp.route('/<int:id>/action/<action>')
@login_required
def action(id, action):
    order = Order.query.get_or_404(id)

    # 权限检查
    role = session['role']
    user_id = session['user_id']

    valid_actions = {
        'confirm': {
            'from': 'pending',
            'to': 'confirmed',
            'role': 'merchant',
            'check_restaurant': True,
            'msg': '已接单',
        },
        'cancel': {
            'from': ['pending', 'confirmed'],
            'to': 'cancelled',
            'role': '*',  # 顾客或商家都可以取消
            'check_restaurant': True,
            'msg': '订单已取消',
        },
        'prepare': {
            'from': 'confirmed',
            'to': 'preparing',
            'role': 'merchant',
            'check_restaurant': True,
            'msg': '开始备餐',
        },
        'ready': {
            'from': 'preparing',
            'to': 'delivering',
            'role': 'merchant',
            'check_restaurant': True,
            'msg': '已准备好，等待骑手取餐',
        },
    }

    if action not in valid_actions:
        flash('无效操作', 'danger')
        return redirect(url_for('order.my_orders'))

    spec = valid_actions[action]
    from_statuses = spec['from'] if isinstance(spec['from'], list) else [spec['from']]

    if order.status not in from_statuses:
        flash(f'当前订单状态为「{order.status}」，无法执行此操作', 'warning')
        return redirect(url_for('order.my_orders'))

    if spec['role'] != '*' and role != spec['role']:
        flash('无权操作', 'danger')
        return redirect(url_for('order.my_orders'))

    if spec.get('check_restaurant') and role == 'merchant':
        restaurant = Restaurant.query.filter_by(owner_id=user_id).first()
        if not restaurant or order.restaurant_id != restaurant.restaurant_id:
            flash('无权操作此订单', 'danger')
            return redirect(url_for('order.my_orders'))

    if action == 'cancel' and role == 'customer' and order.customer_id != user_id:
        flash('无权操作此订单', 'danger')
        return redirect(url_for('order.my_orders'))

    order.status = spec['to']
    db.session.commit()
    flash(spec['msg'], 'success')
    return redirect(url_for('order.my_orders'))


# ============================================================
# 评价
# ============================================================
@order_bp.route('/<int:id>/review', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def review(id):
    order = Order.query.get_or_404(id)
    if order.customer_id != session['user_id']:
        flash('无权操作', 'danger')
        return redirect(url_for('order.my_orders'))
    if order.status != 'delivered':
        flash('只能评价已完成的订单', 'warning')
        return redirect(url_for('order.my_orders'))
    if order.review:
        flash('该订单已评价', 'info')
        return redirect(url_for('order.my_orders'))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            order_id=id,
            customer_id=session['user_id'],
            restaurant_id=order.restaurant_id,
            rating=form.rating.data,
            comment=form.comment.data or None,
        )
        db.session.add(review)
        db.session.commit()
        flash('评价提交成功！', 'success')
        return redirect(url_for('order.my_orders'))

    return render_template('order/review.html', form=form, order=order)
