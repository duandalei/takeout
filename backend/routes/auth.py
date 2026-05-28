import hashlib
import secrets
from flask import Blueprint, request, jsonify
from models.user import find_by_phone, find_by_id, create

auth_bp = Blueprint("auth", __name__)

# token -> {"user_id": int, "role": str}
tokens = {}


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token():
    return secrets.token_hex(32)


def get_user_id_from_token():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        entry = tokens.get(auth[7:])
        return entry["user_id"] if entry else None
    return None


def get_current_role():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        entry = tokens.get(auth[7:])
        return entry["role"] if entry else None
    return None


def require_role(*allowed_roles):
    """返回 (user_id, None) 或 (None, (error_response, status_code))"""
    user_id = get_user_id_from_token()
    if not user_id:
        return None, (jsonify({"error": "未登录"}), 401)
    role = get_current_role()
    if role not in allowed_roles:
        return None, (jsonify({"error": "无权限访问"}), 403)
    return user_id, None


def require_login():
    """返回 (user_id, None, None) 或 (None, error_response, status_code)"""
    user_id = get_user_id_from_token()
    if not user_id:
        return None, jsonify({"error": "未登录"}), 401
    return user_id, None, None


VALID_ROLES = ("customer", "rider", "merchant")


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    phone = data.get("phone", "").strip()
    password = data.get("password", "").strip()
    nickname = data.get("nickname", "").strip()
    role = data.get("role", "customer").strip()

    if role not in VALID_ROLES:
        return jsonify({"error": "角色无效"}), 400
    if not phone or not password or not nickname:
        return jsonify({"error": "手机号、密码和昵称不能为空"}), 400
    if len(phone) != 11 or not phone.isdigit():
        return jsonify({"error": "手机号格式不正确"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码长度不能少于6位"}), 400

    existing = find_by_phone(phone)
    if existing:
        return jsonify({"error": "该手机号已注册"}), 409

    user_id = create(phone, hash_password(password), nickname, role)
    token = generate_token()
    tokens[token] = {"user_id": user_id, "role": role}

    return jsonify({
        "token": token,
        "user": {"user_id": user_id, "phone": phone, "nickname": nickname, "role": role},
    }), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    phone = data.get("phone", "").strip()
    password = data.get("password", "").strip()

    if not phone or not password:
        return jsonify({"error": "手机号和密码不能为空"}), 400

    user = find_by_phone(phone)
    if not user or user["password_hash"] != hash_password(password):
        return jsonify({"error": "手机号或密码错误"}), 401

    role = user.get("role", "customer")
    token = generate_token()
    tokens[token] = {"user_id": user["user_id"], "role": role}

    return jsonify({
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "phone": user["phone"],
            "nickname": user["nickname"],
            "avatar_url": user["avatar_url"],
            "role": role,
        },
    })


@auth_bp.route("/api/auth/me", methods=["GET"])
def me():
    user_id = get_user_id_from_token()
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    user = find_by_id(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify({
        "user_id": user["user_id"],
        "phone": user["phone"],
        "nickname": user["nickname"],
        "avatar_url": user["avatar_url"],
        "role": user.get("role", "customer"),
    })
