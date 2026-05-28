from flask import Blueprint, jsonify
from models.dish import find_by_id

dishes_bp = Blueprint("dishes", __name__)


@dishes_bp.route("/api/dishes/<int:dish_id>", methods=["GET"])
def get_dish(dish_id):
    dish = find_by_id(dish_id)
    if not dish:
        return jsonify({"error": "菜品不存在"}), 404
    return jsonify(dish)
