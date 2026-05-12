import random
import string
import os
from datetime import datetime, timedelta
from flask_mail import Message
from app.extensions import mail, db
from app.models import EmailVerification


def generate_code():
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(email):
    code = generate_code()
    record = EmailVerification(
        email=email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.session.add(record)
    db.session.commit()

    msg = Message(
        '【摄影博客】邮箱验证码',
        recipients=[email],
        body=f'您的验证码是：{code}，有效期 10 分钟。'
    )
    mail.send(msg)


def save_photo(file):
    """保存上传的照片，压缩原图 + 生成缩略图，返回 (文件名, 缩略图文件名)"""
    from PIL import Image

    ext = os.path.splitext(file.filename)[1].lower()
    allowed = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    if ext not in allowed:
        raise ValueError('不支持的文件格式')

    name = ''.join(random.choices(string.ascii_letters + string.digits, k=32)) + '.jpg'
    filepath = os.path.join('app/static/uploads', name)

    img = Image.open(file)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # 压缩原图：长边最大 1600px
    img.thumbnail((1600, 1600))
    img.save(filepath, 'JPEG', quality=85)

    # 生成缩略图：长边最大 400px
    thumb_name = 'thumb_' + name.rsplit('.', 1)[0] + '.jpg'
    thumb_path = os.path.join('app/static/uploads', thumb_name)
    img.thumbnail((400, 400))
    img.save(thumb_path, 'JPEG', quality=75)

    return name, thumb_name
