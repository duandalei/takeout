from flask import Blueprint, request, jsonify
from routes.auth import require_login
from models.address import list_by_user, find_by_id, create, update, delete

addresses_bp = Blueprint("addresses", __name__)


@addresses_bp.route("/api/addresses", methods=["GET"])
def get_addresses():
    user_id, err, code = require_login()
    if err:
        return err, code
    return jsonify(list_by_user(user_id))


@addresses_bp.route("/api/addresses", methods=["POST"])
def create_address():
    user_id, err, code = require_login()
    if err:
        return err, code

    data = request.get_json()
    required = ["contact_name", "phone", "detail"]
    for f in required:
        if not data.get(f):
            return jsonify({"error": f"{f} 不能为空"}), 400

    addr_id = create(
        user_id=user_id,
        contact_name=data["contact_name"],
        phone=data["phone"],
        province=data.get("province", ""),
        city=data.get("city", ""),
        district=data.get("district", ""),
        detail=data["detail"],
        is_default=data.get("is_default", 0),
    )
    return jsonify({"address_id": addr_id}), 201


@addresses_bp.route("/api/addresses/<int:address_id>", methods=["PUT"])
def update_address(address_id):
    user_id, err, code = require_login()
    if err:
        return err, code

    addr = find_by_id(address_id)
    if not addr or addr["user_id"] != user_id:
        return jsonify({"error": "地址不存在"}), 404

    data = request.get_json()
    update(address_id, user_id, **data)
    return jsonify({"message": "更新成功"})


@addresses_bp.route("/api/addresses/<int:address_id>", methods=["DELETE"])
def delete_address(address_id):
    user_id, err, code = require_login()
    if err:
        return err, code

    addr = find_by_id(address_id)
    if not addr or addr["user_id"] != user_id:
        return jsonify({"error": "地址不存在"}), 404

    delete(address_id, user_id)
    return jsonify({"message": "删除成功"})
