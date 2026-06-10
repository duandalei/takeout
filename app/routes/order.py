"""Order routes: create / list / detail / state transitions / review."""

import json
from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.models import db, Order, OrderItem, MenuItem, Restaurant, Review
from app.forms import OrderForm, ReviewForm
from app.routes.auth import login_required, role_required
from flask import current_app
from app.domain.order_state import OrderState

order_bp = Blueprint('order', __name__)


def _actor():
    """Build actor dict from session for OrderState.transition()."""
    return {'user_id': session.get('user_id'), 'role': session.get('role')}


# ============================================================
# Create order from restaurant detail page
# ============================================================
@order_bp.route('/create/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def create(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if restaurant.status != 'open':
        flash('该商家已歇业', 'warning')
        return redirect(url_for('restaurant.list_restaurants'))

    items = (
        MenuItem.query
        .filter_by(restaurant_id=restaurant_id, status='available')
        .order_by(MenuItem.category_id, MenuItem.name)
        .all()
    )

    form = OrderForm()
    # Populate restaurant_id so DataRequired validator passes
    if request.method == 'GET':
        form.restaurant_id.data = restaurant_id
    if form.validate_on_submit():
        cart_json = request.form.get('cart_data', '{}')
        try:
            cart = json.loads(cart_json)
        except json.JSONDecodeError:
            cart = {}

        if not cart:
            flash('请至少选择一个菜品', 'warning')
            return redirect(url_for('order.create', restaurant_id=restaurant_id))

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

        delivery_fee = Decimal(str(current_app.config.get('DELIVERY_FEE', '5.00')))

        order = Order(
            customer_id=session['user_id'],
            restaurant_id=restaurant_id,
            delivery_address=form.delivery_address.data,
            status='pending',
            total_amount=total + delivery_fee,
            delivery_fee=delivery_fee,
            note=form.note.data or None,
        )
        order.order_items = order_items
        db.session.add(order)
        db.session.commit()

        flash(f'订单已提交！总计 ¥{total + delivery_fee:.2f} (含配送费 ¥{delivery_fee:.2f})', 'success')
        return redirect(url_for('order.my_orders'))

    return render_template('order/create.html',
                           restaurant=restaurant,
                           items=items,
                           form=form)


# ============================================================
# My orders (role-filtered, optional status filter)
# ============================================================

STATUS_GROUPS = {
    'pending':   ['pending', 'confirmed'],
    'active':    ['preparing', 'ready', 'assigned', 'picked_up'],
    'completed': ['delivered'],
    'cancelled': ['cancelled'],
}

STATUS_TABS = [
    ('all',       '全部'),
    ('pending',   '待处理'),
    ('active',    '进行中'),
    ('completed', '已完成'),
    ('cancelled', '已取消'),
]


@order_bp.route('/my')
@login_required
def my_orders():
    user_id = session['user_id']
    role = session['role']
    status = request.args.get('status', 'all')

    if role == 'customer':
        query = (
            Order.query
            .filter_by(customer_id=user_id)
        )
    elif role == 'merchant':
        restaurant = Restaurant.query.filter_by(owner_id=user_id).first()
        if not restaurant:
            return render_template('order/list.html', orders=[],
                                   status_tabs=STATUS_TABS,
                                   current_status=status,
                                   OrderState=OrderState)
        query = (
            Order.query
            .filter_by(restaurant_id=restaurant.restaurant_id)
        )
    else:
        return render_template('order/list.html', orders=[],
                               status_tabs=STATUS_TABS,
                               current_status=status,
                               OrderState=OrderState)

    # Apply status filter
    if status in STATUS_GROUPS:
        query = query.filter(Order.status.in_(STATUS_GROUPS[status]))

    orders = query.order_by(Order.created_at.desc()).all()

    return render_template('order/list.html', orders=orders,
                           status_tabs=STATUS_TABS,
                           current_status=status,
                           OrderState=OrderState)


# ============================================================
# Order detail
# ============================================================
@order_bp.route('/<int:id>')
@login_required
def detail(id):
    order = Order.query.get_or_404(id)
    return render_template('order/detail.html', order=order,
                           OrderState=OrderState)


# ============================================================
# State transition — single endpoint, delegates to OrderState
# ============================================================
@order_bp.route('/<int:id>/action/<action>')
@login_required
def action(id, action):
    order = Order.query.get_or_404(id)
    actor = _actor()

    result = OrderState.transition(order, action, actor)
    if not result.ok:
        flash(result.error, 'warning')
        return redirect(url_for('order.my_orders'))

    # Apply transition
    order.status = result.new_status

    # Handle side effects
    side = OrderState.side_effect(action)
    if side == 'rider_assigned':
        order.rider_id = session['user_id']
    elif side == 'rider_picked_up':
        from datetime import datetime
        order.pickup_time = datetime.utcnow()
    elif side == 'rider_delivered':
        from datetime import datetime
        order.delivery_time = datetime.utcnow()

    db.session.commit()

    # Flash message
    msgs = {
        'confirm': '已接单', 'cancel': '订单已取消', 'prepare': '开始备餐',
        'ready': '已准备好，等待骑手取餐', 'assign': '接单成功！',
        'pickup': '已取餐，请尽快送达', 'deliver': '已送达！',
    }
    flash(msgs.get(action, '操作成功'), 'success')
    return redirect(url_for('order.my_orders'))


# ============================================================
# Review
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
            rating=form.rating.data,
            comment=form.comment.data or None,
        )
        db.session.add(review)
        db.session.commit()
        flash('评价提交成功！', 'success')
        return redirect(url_for('order.my_orders'))

    return render_template('order/review.html', form=form, order=order)
