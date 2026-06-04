"""配送路由: 待接订单 / 接单 / 取餐 / 送达"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.models import db, Order, Delivery, Restaurant
from app.routes.auth import login_required, role_required

delivery_bp = Blueprint('delivery', __name__)


# ============================================================
# 待接配送订单列表 (骑手视角)
# ============================================================
@delivery_bp.route('/available')
@login_required
@role_required('rider')
def available_orders():
    # 状态为 delivering (商家已备好) 且无骑手接单的订单
    orders = (
        Order.query
        .filter_by(status='delivering', rider_id=None)
        .order_by(Order.created_at.asc())
        .all()
    )
    return render_template('delivery/available.html', orders=orders)


# ============================================================
# 骑手接单
# ============================================================
@delivery_bp.route('/accept/<int:order_id>')
@login_required
@role_required('rider')
def accept(order_id):
    order = Order.query.get_or_404(order_id)

    if order.status != 'delivering':
        flash('此订单当前不可接单', 'warning')
        return redirect(url_for('delivery.available_orders'))
    if order.rider_id is not None:
        flash('此订单已被其他骑手接单', 'warning')
        return redirect(url_for('delivery.available_orders'))

    # 分配骑手
    order.rider_id = session['user_id']

    # 创建配送记录
    delivery = Delivery(
        order_id=order_id,
        rider_id=session['user_id'],
        status='assigned',
    )
    db.session.add(delivery)
    db.session.commit()

    flash('接单成功！', 'success')
    return redirect(url_for('delivery.my_deliveries'))


# ============================================================
# 我的配送
# ============================================================
@delivery_bp.route('/my')
@login_required
@role_required('rider')
def my_deliveries():
    deliveries = (
        Delivery.query
        .filter_by(rider_id=session['user_id'])
        .order_by(Delivery.pickup_time.asc(),
                  Delivery.delivery_id.desc())
        .all()
    )
    return render_template('delivery/my.html', deliveries=deliveries)


# ============================================================
# 取餐
# ============================================================
@delivery_bp.route('/pickup/<int:delivery_id>')
@login_required
@role_required('rider')
def pickup(delivery_id):
    delivery = Delivery.query.get_or_404(delivery_id)
    if delivery.rider_id != session['user_id']:
        flash('无权操作', 'danger')
        return redirect(url_for('delivery.my_deliveries'))
    if delivery.status != 'assigned':
        flash('当前状态不可取餐', 'warning')
        return redirect(url_for('delivery.my_deliveries'))

    delivery.status = 'picked_up'
    delivery.pickup_time = datetime.utcnow()
    db.session.commit()

    flash('已取餐，请尽快送达', 'success')
    return redirect(url_for('delivery.my_deliveries'))


# ============================================================
# 送达
# ============================================================
@delivery_bp.route('/deliver/<int:delivery_id>')
@login_required
@role_required('rider')
def deliver(delivery_id):
    delivery = Delivery.query.get_or_404(delivery_id)
    if delivery.rider_id != session['user_id']:
        flash('无权操作', 'danger')
        return redirect(url_for('delivery.my_deliveries'))
    if delivery.status != 'picked_up':
        flash('请先取餐', 'warning')
        return redirect(url_for('delivery.my_deliveries'))

    delivery.status = 'delivered'
    delivery.delivery_time = datetime.utcnow()

    # 同步更新订单状态
    order = delivery.order
    order.status = 'delivered'
    db.session.commit()

    flash('已送达！', 'success')
    return redirect(url_for('delivery.my_deliveries'))
