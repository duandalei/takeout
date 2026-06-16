"""Delivery routes: available orders / accept / pickup / deliver."""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, session
from app.models import db, Order
from app.domain.auth import require
from app.domain.order_state import OrderState, get_actor

delivery_bp = Blueprint('delivery', __name__)


# ============================================================
# Available orders for riders to accept
# ============================================================
@delivery_bp.route('/available')
@require(role='rider')
def available_orders():
    orders = (
        Order.query
        .filter_by(status='ready', rider_id=None)
        .order_by(Order.created_at.asc())
        .all()
    )
    return render_template('delivery/available.html', orders=orders, OrderState=OrderState)


# ============================================================
# Rider accepts an order
# ============================================================
@delivery_bp.route('/accept/<int:order_id>')
@require(role='rider')
def accept(order_id):
    order = Order.query.get_or_404(order_id)
    actor = get_actor()

    result = OrderState.transition(order, 'assign', actor)
    if not result.ok:
        flash(result.error, 'warning')
        return redirect(url_for('delivery.available_orders'))

    order.status = result.new_status
    order.rider_id = session['user_id']
    db.session.commit()

    flash('接单成功！', 'success')
    return redirect(url_for('delivery.my_deliveries'))


# ============================================================
# Rider's deliveries
# ============================================================
@delivery_bp.route('/my')
@require(role='rider')
def my_deliveries():
    orders = (
        Order.query
        .filter(Order.rider_id == session['user_id'])
        .filter(Order.status.in_(['assigned', 'picked_up', 'delivered']))
        .order_by(Order.pickup_time.asc(), Order.order_id.desc())
        .all()
    )
    return render_template('delivery/my.html', orders=orders, OrderState=OrderState)


# ============================================================
# Rider picks up the order
# ============================================================
@delivery_bp.route('/pickup/<int:order_id>')
@require(role='rider')
def pickup(order_id):
    order = Order.query.get_or_404(order_id)
    actor = get_actor()

    result = OrderState.transition(order, 'pickup', actor)
    if not result.ok:
        flash(result.error, 'warning')
        return redirect(url_for('delivery.my_deliveries'))

    order.status = result.new_status
    order.pickup_time = datetime.utcnow()
    db.session.commit()

    flash('已取餐，请尽快送达', 'success')
    return redirect(url_for('delivery.my_deliveries'))


# ============================================================
# Rider delivers the order
# ============================================================
@delivery_bp.route('/deliver/<int:order_id>')
@require(role='rider')
def deliver(order_id):
    order = Order.query.get_or_404(order_id)
    actor = get_actor()

    result = OrderState.transition(order, 'deliver', actor)
    if not result.ok:
        flash(result.error, 'warning')
        return redirect(url_for('delivery.my_deliveries'))

    order.status = result.new_status
    order.delivery_time = datetime.utcnow()
    db.session.commit()

    flash('已送达！', 'success')
    return redirect(url_for('delivery.my_deliveries'))
