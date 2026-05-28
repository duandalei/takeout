from datetime import datetime
from flask import Blueprint, request, jsonify
from routes.auth import get_user_id_from_token, require_role
from models.rider import find_by_id, get_pending_orders, set_status, find_by_user_id, get_available_orders
from models.order import find_by_id as find_order, update_status, list_by_rider, assign_rider, get_items

riders_bp = Blueprint("riders", __name__)


@riders_bp.route("/api/rider/orders", methods=["GET"])
def rider_orders():
    user_id, err = require_role("rider")
    if err:
        return err
    rider = find_by_user_id(user_id)
    if not rider:
        return jsonify({"error": "骑手信息不存在"}), 404
    orders = list_by_rider(rider["rider_id"])
    for o in orders:
        o["items"] = get_items(o["order_id"])
    return jsonify(orders)


@riders_bp.route("/api/rider/orders/<int:order_id>/deliver", methods=["PUT"])
def deliver_order(order_id):
    user_id, err = require_role("rider")
    if err:
        return err
    rider = find_by_user_id(user_id)
    if not rider:
        return jsonify({"error": "骑手信息不存在"}), 404

    order = find_order(order_id)
    if not order:
        return jsonify({"error": "订单不存在"}), 404
    if order["rider_id"] != rider["rider_id"]:
        return jsonify({"error": "这不是您的订单"}), 403
    if order["status"] != 3:
        return jsonify({"error": "订单状态不允许此操作"}), 400

    update_status(order_id, 4, delivered_at=datetime.now())

    pending = get_pending_orders(rider["rider_id"])
    remaining = [o for o in pending if o["order_id"] != order_id]
    if not remaining:
        set_status(rider["rider_id"], 1)

    return jsonify({"message": "已确认送达"})


@riders_bp.route("/api/rider/available", methods=["GET"])
def available_orders():
    """骑手查看所有可接的订单"""
    user_id, err = require_role("rider")
    if err:
        return err
    orders = get_available_orders()
    for o in orders:
        o["items"] = get_items(o["order_id"])
    return jsonify(orders)


@riders_bp.route("/api/rider/orders/<int:order_id>/accept", methods=["PUT"])
def accept_order(order_id):
    """骑手接单"""
    user_id, err = require_role("rider")
    if err:
        return err
    rider = find_by_user_id(user_id)
    if not rider:
        return jsonify({"error": "骑手信息不存在"}), 404
    if rider["status"] != 1:
        return jsonify({"error": "您当前不在空闲状态"}), 400

    order = find_order(order_id)
    if not order:
        return jsonify({"error": "订单不存在"}), 404
    if order["status"] != 6:
        return jsonify({"error": "该订单已被接单或已取消"}), 400
    if order["rider_id"] is not None:
        return jsonify({"error": "该订单已有骑手接单"}), 400

    assign_rider(order_id, rider["rider_id"])
    set_status(rider["rider_id"], 2)
    update_status(order_id, 3)

    return jsonify({"message": "接单成功"})

