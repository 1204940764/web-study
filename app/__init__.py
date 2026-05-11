from flask import Flask
from config import Config
from app.extensions import db, login_manager, mail


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.photos.routes import photos_bp
    from app.user.routes import user_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(photos_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.models import Announcement, AnnouncementView
    from flask_login import current_user

    @app.context_processor
    def inject_unread_announcement():
        if current_user.is_authenticated:
            latest = Announcement.query.order_by(Announcement.created_at.desc()).first()
            if latest:
                seen = AnnouncementView.query.filter_by(
                    user_id=current_user.id, announcement_id=latest.id
                ).first()
                if not seen:
                    return {'unread_announcement': latest}
        return {'unread_announcement': None}

    return app
