from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Photo, Comment, Announcement, AnnouncementView, Suggestion, Config
from app.decorators import admin_required, super_admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    ann_count = Announcement.query.count()
    review_enabled = Config.get('review_enabled', '1') == '1'
    return render_template('admin/dashboard.html',
                           user_count=User.query.count(),
                           photo_count=Photo.query.count(),
                           comment_count=Comment.query.count(),
                           pending_count=Photo.query.filter_by(status='pending').count(),
                           ann_count=ann_count,
                           review_enabled=review_enabled)


@admin_bp.route('/toggle-review', methods=['POST'])
@login_required
@admin_required
def toggle_review():
    current = Config.get('review_enabled', '1')
    new_value = '0' if current == '1' else '1'
    Config.set('review_enabled', new_value)
    db.session.commit()
    if new_value == '0':
        flash('审核功能已关闭，所有用户可直接发布照片', 'success')
    else:
        flash('审核功能已开启，用户上传的照片需审核后才会公开展示', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('不能删除自己的账号', 'error')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    if user.is_super_admin:
        flash('不能删除超级管理员', 'error')
        return redirect(url_for('admin.users'))
    Comment.query.filter_by(user_id=user_id).delete()
    Photo.query.filter_by(user_id=user_id).delete()
    Suggestion.query.filter_by(user_id=user_id).delete()
    AnnouncementView.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash('用户已删除', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-mute', methods=['POST'])
@login_required
@admin_required
def toggle_mute(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_super_admin or (user.is_admin and not current_user.is_super_admin):
        flash('不能对此用户执行此操作', 'error')
        return redirect(url_for('admin.users'))
    user.is_muted = not user.is_muted
    db.session.commit()
    action = '禁言' if user.is_muted else '解除禁言'
    flash(f'用户 {user.email} 已{action}', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-upload-ban', methods=['POST'])
@login_required
@admin_required
def toggle_upload_ban(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_super_admin or (user.is_admin and not current_user.is_super_admin):
        flash('不能对此用户执行此操作', 'error')
        return redirect(url_for('admin.users'))
    user.is_upload_banned = not user.is_upload_banned
    db.session.commit()
    action = '禁止发布' if user.is_upload_banned else '解除发布限制'
    flash(f'用户 {user.email} 已{action}', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/set-role', methods=['POST'])
@login_required
@super_admin_required
def set_role(user_id):
    if user_id == current_user.id:
        flash('不能修改自己的角色', 'error')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', '').strip()
    if new_role not in ('user', 'admin'):
        flash('无效的角色', 'error')
        return redirect(url_for('admin.users'))

    if user.is_super_admin:
        flash('不能修改超级管理员的角色', 'error')
        return redirect(url_for('admin.users'))

    role_names = {'user': '普通用户', 'admin': '管理员'}
    user.role = new_role
    db.session.commit()
    flash(f'用户 {user.email} 已设为{role_names[new_role]}', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/photos')
@login_required
@admin_required
def photos():
    photos = Photo.query.order_by(Photo.created_at.desc()).all()
    return render_template('admin/photos.html', photos=photos)


@admin_bp.route('/photos/<int:photo_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.author.is_super_admin and not current_user.is_super_admin:
        flash('不能审批超级管理员的照片', 'error')
        return redirect(url_for('admin.photos'))
    photo.status = 'approved'
    db.session.commit()
    flash('照片已通过审核', 'success')
    return redirect(url_for('admin.photos'))


@admin_bp.route('/photos/<int:photo_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if photo.author.is_super_admin and not current_user.is_super_admin:
        flash('不能拒绝超级管理员的照片', 'error')
        return redirect(url_for('admin.photos'))
    photo.status = 'rejected'
    db.session.commit()
    flash('照片已拒绝', 'success')
    return redirect(url_for('admin.photos'))


@admin_bp.route('/photos/<int:photo_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_photo(photo_id):
    import os
    photo = Photo.query.get_or_404(photo_id)
    if photo.author.is_super_admin and not current_user.is_super_admin:
        flash('不能删除超级管理员的照片', 'error')
        return redirect(url_for('admin.photos'))
    # 删除磁盘文件
    base = 'app/static/uploads'
    for f in [photo.filename, photo.thumb_filename]:
        if f:
            path = os.path.join(base, f)
            if os.path.exists(path):
                os.remove(path)
    # 删除关联评论
    Comment.query.filter_by(photo_id=photo_id).delete()
    db.session.delete(photo)
    db.session.commit()
    flash('照片已删除', 'success')
    return redirect(url_for('admin.photos'))


@admin_bp.route('/comments')
@login_required
@admin_required
def comments():
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/comments.html', comments=comments)


@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('admin.comments'))


@admin_bp.route('/suggestions')
@login_required
@admin_required
def suggestions():
    suggestions = Suggestion.query.order_by(Suggestion.created_at.desc()).all()
    return render_template('admin/suggestions.html', suggestions=suggestions)


@admin_bp.route('/announcements')
@login_required
@admin_required
def announcements():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=anns)


@admin_bp.route('/announcements/create', methods=['POST'])
@login_required
@admin_required
def create_announcement():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    if title and content:
        ann = Announcement(title=title, content=content)
        db.session.add(ann)
        db.session.commit()
        flash('公告已发布', 'success')
    return redirect(url_for('admin.announcements'))


@admin_bp.route('/announcements/<int:ann_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    AnnouncementView.query.filter_by(announcement_id=ann_id).delete()
    db.session.delete(ann)
    db.session.commit()
    flash('公告已删除', 'success')
    return redirect(url_for('admin.announcements'))
