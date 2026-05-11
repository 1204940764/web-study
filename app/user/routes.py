from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            flash('用户名不能为空', 'error')
        else:
            current_user.username = username
            db.session.commit()
            flash('用户名修改成功', 'success')
    return render_template('profile.html')


@user_bp.route('/profile/photos')
@login_required
def my_photos():
    photos = current_user.photos.order_by(
        current_user.photos.any().created_at.desc()
    ).all()
    return render_template('my_photos.html', photos=photos)
