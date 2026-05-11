from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, EmailVerification
from app.utils import send_verification_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        code = request.form.get('code', '').strip()

        error = None
        if not email or '@' not in email:
            error = '请输入有效的邮箱地址'
        elif User.query.filter_by(email=email).first():
            error = '该邮箱已注册'
        elif not username:
            error = '请输入用户名'
        elif len(password) < 6:
            error = '密码至少 6 位'
        elif not code:
            error = '请输入验证码'
        else:
            v = EmailVerification.valid_code(email, code)
            if not v:
                error = '验证码错误或已过期'

        if error:
            flash(error, 'error')
        else:
            user = User(email=email, username=username)
            user.set_password(password)
            v.mark_used()
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('注册成功！', 'success')
            return redirect(url_for('main.index'))

    return render_template('register.html')


@auth_bp.route('/register/send-code', methods=['POST'])
def send_code():
    email = request.form.get('email', '').strip()
    if not email or User.query.filter_by(email=email).first():
        return {'ok': False, 'msg': '邮箱不可用'}
    try:
        send_verification_email(email)
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'msg': '发送失败，请检查邮件服务配置'}


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('登录成功！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))

        flash('邮箱或密码错误', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_pw = request.form.get('new_password', '').strip()
        code = request.form.get('code', '').strip()

        error = None
        if not email or '@' not in email:
            error = '请输入有效的邮箱地址'
        elif not User.query.filter_by(email=email).first():
            error = '该邮箱未注册'
        elif len(new_pw) < 6:
            error = '密码至少 6 位'
        elif not code:
            error = '请输入验证码'
        else:
            v = EmailVerification.valid_code(email, code)
            if not v:
                error = '验证码错误或已过期'

        if error:
            flash(error, 'error')
        else:
            user = User.query.filter_by(email=email).first()
            user.set_password(new_pw)
            v.mark_used()
            db.session.commit()
            flash('密码重置成功，请登录', 'success')
            return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@auth_bp.route('/forgot-password/send-code', methods=['POST'])
def send_forgot_code():
    email = request.form.get('email', '').strip()
    if not email or not User.query.filter_by(email=email).first():
        return {'ok': False, 'msg': '该邮箱未注册'}
    try:
        send_verification_email(email)
        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'msg': '发送失败，请检查邮件服务配置'}
