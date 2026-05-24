from flask import Blueprint, request, jsonify
from routes.auth import get_user_id_from_token
from models.review import create, list_by_merchant, get_by_order
from models.order import find_by_id, update_status

reviews_bp = Blueprint("reviews", __name__)


def _get_user_id():
    user_id = get_user_id_from_token()
    if not user_id:
        return None, jsonify({"error": "未登录"}), 401
    return user_id, None, None


@reviews_bp.route("/api/reviews", methods=["POST"])
def create_review():
    """提交评价"""
    user_id, err, code = _get_user_id()
    if err:
        return err, code

    data = request.get_json()
    order_id = data.get("order_id")
    rating = data.get("rating")
    content = data.get("content", "")

    if not order_id or not rating:
        return jsonify({"error": "订单ID和评分不能为空"}), 400
    if rating < 1 or rating > 5:
        return jsonify({"error": "评分范围1-5"}), 400

    order = find_by_id(order_id)
    if not order or order["user_id"] != user_id:
        return jsonify({"error": "订单不存在"}), 404
    if order["status"] != 4:
        return jsonify({"error": "只能评价已送达的订单"}), 400

    existing = get_by_order(order_id)
    if existing:
        return jsonify({"error": "该订单已评价"}), 409

    review_id = create(
        order_id=order_id,
        user_id=user_id,
        merchant_id=order["merchant_id"],
        rating=rating,
        content=content,
    )
    return jsonify({"review_id": review_id}), 201


@reviews_bp.route("/api/reviews/merchant/<int:merchant_id>", methods=["GET"])
def get_merchant_reviews(merchant_id):
    reviews = list_by_merchant(merchant_id)
    return jsonify(reviews)
