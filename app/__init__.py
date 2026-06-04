"""Flask 应用工厂"""

from flask import Flask, render_template, session
from app.config import DevelopmentConfig
from app.models import db


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.restaurant import restaurant_bp
    from app.routes.menu import menu_bp
    from app.routes.order import order_bp
    from app.routes.delivery import delivery_bp

    app.register_blueprint(auth_bp,       url_prefix='/auth')
    app.register_blueprint(restaurant_bp, url_prefix='/restaurant')
    app.register_blueprint(menu_bp,       url_prefix='/menu')
    app.register_blueprint(order_bp,      url_prefix='/order')
    app.register_blueprint(delivery_bp,   url_prefix='/delivery')

    # 首页
    @app.route('/')
    def home():
        return render_template('index.html')

    # 上下文处理器 — 注入全局变量到模板
    @app.context_processor
    def inject_user():
        current = None
        if session.get('user_id'):
            current = {
                'user_id':   session.get('user_id'),
                'username':  session.get('username'),
                'role':      session.get('role'),
                'real_name': session.get('real_name'),
            }
        return {'current_user': current}

    return app
