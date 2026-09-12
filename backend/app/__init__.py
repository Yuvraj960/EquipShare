from flask import Flask, request
from .config import Config
from .extensions import db, migrate, cors, security, celery
from .models import User, Role
from flask_security import login_user
from flask_security.core import parse_auth_token

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    # Allow all origins for dev
    cors.init_app(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True, "allow_headers": ["Content-Type", "Authentication-Token"]}})

    # Flask-Security setup
    from flask_security import SQLAlchemyUserDatastore
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)

    # Automatically authenticate requests providing Authentication-Token header
    @app.before_request
    def load_token_user():
        token = request.headers.get('Authentication-Token')
        if token:
            try:
                data = parse_auth_token(token)
                uid = data.get('uid')
                if uid:
                    user = User.query.filter_by(fs_uniquifier=uid).first()
                    if user and user.active:
                        login_user(user)
            except Exception:
                pass

    # Celery
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)

    # Register blueprints
    from .api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    return app
