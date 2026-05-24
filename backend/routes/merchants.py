from flask import Blueprint, jsonify
from models.merchant import list_all, find_by_id, get_menu

merchants_bp = Blueprint("merchants", __name__)


@merchants_bp.route("/api/merchants", methods=["GET"])
def get_merchants():
    merchants = list_all()
    return jsonify(merchants)


@merchants_bp.route("/api/merchants/<int:merchant_id>", methods=["GET"])
def get_merchant(merchant_id):
    merchant = find_by_id(merchant_id)
    if not merchant:
        return jsonify({"error": "商家不存在"}), 404
    menu = get_menu(merchant_id)
    merchant["menu"] = menu
    return jsonify(merchant)


@merchants_bp.route("/api/merchants/<int:merchant_id>/menu", methods=["GET"])
def get_merchant_menu(merchant_id):
    menu = get_menu(merchant_id)
    return jsonify(menu)
