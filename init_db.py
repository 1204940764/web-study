"""初始化数据库表 + 创建管理员账号"""
from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    print('数据库表创建完成')

    admin_email = '1204940764@qq.com'
    if not User.query.filter_by(email=admin_email).first():
        admin = User(email=admin_email, username='管理员', is_admin=True)
        admin.set_password('ljw20040420')
        db.session.add(admin)
        db.session.commit()
        print(f'管理员账号已创建: {admin_email} / ljw20040420')
    else:
        print('管理员账号已存在')
