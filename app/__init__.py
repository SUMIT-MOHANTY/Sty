from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from app.controllers.main import main_bp
    app.register_blueprint(main_bp)

    from app.controllers.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.controllers.application import application_bp
    app.register_blueprint(application_bp, url_prefix='/applications')

    # Error handlers
    from app.controllers.errors import register_error_handlers
    register_error_handlers(app)

    return app
