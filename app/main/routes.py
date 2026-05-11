from flask import Blueprint, render_template, request
from app.models import Photo, Comment

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    photos = Photo.query.filter_by(status='approved')\
        .order_by(Photo.created_at.desc())\
        .paginate(page=page, per_page=20)
    return render_template('index.html', photos=photos)


@main_bp.route('/photo/<int:photo_id>')
def photo_detail(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    comments = photo.comments.order_by(Comment.created_at.desc()).all()
    return render_template('photo_detail.html', photo=photo, comments=comments)


@main_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    photos = []
    if q:
        photos = Photo.query.filter_by(status='approved')\
            .filter(
                Photo.title.contains(q) | Photo.description.contains(q)
            ).order_by(Photo.created_at.desc()).limit(50).all()
    return render_template('search.html', photos=photos, query=q)
