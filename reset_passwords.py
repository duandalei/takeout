"""重置所有用户密码为 123456
运行前请确保已修改 app/config.py 中的数据库连接信息
"""
from werkzeug.security import generate_password_hash
from app import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    users = User.query.all()
    new_hash = generate_password_hash('123456')
    for u in users:
        u.password_hash = new_hash
        print(f'{u.username} ({u.role}) -> 密码已重置')
    db.session.commit()
    print(f'\n完成！共 {len(users)} 个用户，密码统一为: 123456')
