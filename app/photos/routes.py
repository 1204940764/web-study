import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Photo, Comment
from app.utils import save_photo

photos_bp = Blueprint('photos', __name__)


@photos_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if current_user.is_upload_banned:
            flash('你已被禁止发布照片', 'error')
            return redirect(url_for('user.my_photos'))

        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        file = request.files.get('photo')

        if not title:
            flash('请输入照片标题', 'error')
        elif not file or not file.filename:
            flash('请选择照片', 'error')
        else:
            try:
                filename = save_photo(file)
                photo = Photo(
                    user_id=current_user.id,
                    title=title,
                    description=description,
                    filename=filename
                )
                db.session.add(photo)
                db.session.commit()
                flash('上传成功，等待管理员审核', 'success')
                return redirect(url_for('user.my_photos'))
            except ValueError as e:
                flash(str(e), 'error')

    return render_template('upload.html')


@photos_bp.route('/photo/<int:photo_id>/comment', methods=['POST'])
@login_required
def add_comment(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    content = request.form.get('content', '').strip()

    if current_user.is_muted:
        flash('你已被禁言，无法发表评论', 'error')
        return redirect(url_for('main.photo_detail', photo_id=photo_id))

    if not content:
        flash('评论不能为空', 'error')
    else:
        comment = Comment(user_id=current_user.id, photo_id=photo_id, content=content)
        db.session.add(comment)
        db.session.commit()
        flash('评论发表成功', 'success')

    return redirect(url_for('main.photo_detail', photo_id=photo_id))


@photos_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    photo_id = comment.photo_id
    if current_user.id != comment.user_id and not current_user.is_admin:
        flash('无权删除此评论', 'error')
        return redirect(url_for('main.photo_detail', photo_id=photo_id))
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('main.photo_detail', photo_id=photo_id))
