from datetime import datetime
from flask import Blueprint, request, jsonify
from routes.auth import get_user_id_from_token, require_role
from models.order import (
    create, find_by_id, get_items, list_by_user,
    list_by_merchant, update_status,
)
from models.merchant import find_by_id as find_merchant, find_by_user_id as find_merchant_by_user_id
from models.address import find_by_id as find_address
from models.dish import find_by_id as find_dish
from models.review import get_by_order

orders_bp = Blueprint("orders", __name__)


def _get_customer():
    return require_role("customer")


@orders_bp.route("/api/orders", methods=["POST"])
def place_order():
    user_id, err = _get_customer()
    if err:
        return err

    data = request.get_json()
    merchant_id = data.get("merchant_id")
    address_id = data.get("address_id")
    items = data.get("items", [])
    remark = data.get("remark", "")

    if not merchant_id or not address_id or not items:
        return jsonify({"error": "商家、地址和菜品不能为空"}), 400

    merchant = find_merchant(merchant_id)
    if not merchant or merchant["status"] != 1:
        return jsonify({"error": "商家不存在或已休息"}), 400

    addr = find_address(address_id)
    if not addr or addr["user_id"] != user_id:
        return jsonify({"error": "地址不存在"}), 400

    total_price = 0
    order_items = []
    for item in items:
        dish = find_dish(item["dish_id"])
        if not dish or dish["status"] != 1:
            return jsonify({"error": f"菜品 {item.get('dish_id')} 不存在或已下架"}), 400
        qty = item.get("quantity", 1)
        if qty < 1:
            return jsonify({"error": "数量至少为1"}), 400
        total_price += float(dish["price"]) * qty
        order_items.append({
            "dish_id": dish["dish_id"],
            "dish_name": dish["name"],
            "dish_price": float(dish["price"]),
            "quantity": qty,
        })

    delivery_fee = float(merchant["delivery_fee"])
    actual_amount = total_price + delivery_fee

    if total_price < float(merchant["min_delivery_price"]):
        return jsonify({
            "error": f"未达起送价 {merchant['min_delivery_price']} 元"
        }), 400

    order_id = create(
        user_id, merchant_id, address_id,
        total_price, delivery_fee, actual_amount,
        remark, order_items,
    )

    return jsonify({"order_id": order_id, "actual_amount": actual_amount}), 201


@orders_bp.route("/api/orders", methods=["GET"])
def get_my_orders():
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    orders = list_by_user(user_id)
    return jsonify(orders)


@orders_bp.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({"error": "未登录"}), 401

    order = find_by_id(order_id)
    if not order:
        return jsonify({"error": "订单不存在"}), 404

    order["items"] = get_items(order_id)
    order["review"] = get_by_order(order_id)
    return jsonify(order)


@orders_bp.route("/api/orders/<int:order_id>/pay", methods=["PUT"])
def pay_order(order_id):
    user_id, err = _get_customer()
    if err:
        return err

    order = find_by_id(order_id)
    if not order or order["user_id"] != user_id:
        return jsonify({"error": "订单不存在"}), 404
    if order["status"] != 1:
        return jsonify({"error": "订单状态不允许支付"}), 400

    update_status(order_id, 2, paid_at=datetime.now())
    return jsonify({"message": "支付成功"})


@orders_bp.route("/api/orders/<int:order_id>/cancel", methods=["PUT"])
def cancel_order(order_id):
    user_id, err = _get_customer()
    if err:
        return err

    order = find_by_id(order_id)
    if not order or order["user_id"] != user_id:
        return jsonify({"error": "订单不存在"}), 404
    if order["status"] not in (1, 2, 6):
        return jsonify({"error": "当前状态不允许取消"}), 400

    update_status(order_id, 5)
    return jsonify({"message": "已取消"})


@orders_bp.route("/api/merchant/orders", methods=["GET"])
def merchant_orders():
    user_id, err = require_role("merchant")
    if err:
        return err
    merchant = find_merchant_by_user_id(user_id)
    if not merchant:
        return jsonify({"error": "商家信息不存在"}), 404

    status = request.args.get("status", type=int)
    orders = list_by_merchant(merchant["merchant_id"], status)
    return jsonify(orders)


@orders_bp.route("/api/merchant/orders/<int:order_id>/accept", methods=["PUT"])
def accept_order(order_id):
    user_id, err = require_role("merchant")
    if err:
        return err
    merchant = find_merchant_by_user_id(user_id)
    if not merchant:
        return jsonify({"error": "商家信息不存在"}), 404

    order = find_by_id(order_id)
    if not order:
        return jsonify({"error": "订单不存在"}), 404
    if order["merchant_id"] != merchant["merchant_id"]:
        return jsonify({"error": "这不是您的订单"}), 403
    if order["status"] != 2:
        return jsonify({"error": "只能接待接单状态的订单"}), 400

    update_status(order_id, 6)

    return jsonify({"message": "已确认订单，等待骑手接单"})
