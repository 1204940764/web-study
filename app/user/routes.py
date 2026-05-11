from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Photo

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


@user_bp.route('/profile/password', methods=['POST'])
@login_required
def change_password():
    old_pw = request.form.get('old_password', '')
    new_pw = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')

    if not old_pw or not new_pw:
        flash('请填写完整', 'error')
        return redirect(url_for('user.profile'))

    if not current_user.check_password(old_pw):
        flash('原密码错误', 'error')
        return redirect(url_for('user.profile'))

    if len(new_pw) < 6:
        flash('新密码至少 6 位', 'error')
        return redirect(url_for('user.profile'))

    if new_pw != confirm_pw:
        flash('两次输入的密码不一致', 'error')
        return redirect(url_for('user.profile'))

    current_user.set_password(new_pw)
    db.session.commit()
    flash('密码修改成功', 'success')
    return redirect(url_for('user.profile'))


@user_bp.route('/profile/photos')
@login_required
def my_photos():
    photos = current_user.photos.order_by(Photo.created_at.desc()).all()
    return render_template('my_photos.html', photos=photos)
