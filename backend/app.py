from flask import Flask
from flask_cors import CORS
from config import SECRET_KEY

from routes.auth import auth_bp
from routes.merchants import merchants_bp
from routes.dishes import dishes_bp
from routes.addresses import addresses_bp
from routes.orders import orders_bp
from routes.reviews import reviews_bp
from routes.riders import riders_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["JSON_AS_ASCII"] = False  # 支持中文输出

    CORS(app, supports_credentials=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(merchants_bp)
    app.register_blueprint(dishes_bp)
    app.register_blueprint(addresses_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(riders_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
