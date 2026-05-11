from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Photo, Comment
from app.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    photo_count = Photo.query.count()
    comment_count = Comment.query.count()
    pending_count = Photo.query.filter_by(status='pending').count()
    return render_template('admin/dashboard.html',
                           user_count=user_count,
                           photo_count=photo_count,
                           comment_count=comment_count,
                           pending_count=pending_count)


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
    Comment.query.filter_by(user_id=user_id).delete()
    Photo.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash('用户已删除', 'success')
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
    photo.status = 'approved'
    db.session.commit()
    flash('照片已通过审核', 'success')
    return redirect(url_for('admin.photos'))


@admin_bp.route('/photos/<int:photo_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo.status = 'rejected'
    db.session.commit()
    flash('照片已拒绝', 'success')
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
