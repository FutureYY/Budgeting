from os import path
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from app.config import Config
from app.models import db
from app import init_bp
from flask_login import LoginManager
from app.auth import auth
from app.views import views


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf = CSRFProtect()
    csrf.init_app(app)

    with app.app_context():
        # Create the tables in the database if they don't exist
        if not path.exists(app.config['DATABASE_NAME']):
            db.create_all()
            print('Created Database!')

        # Login Manager
        Manager_Login = LoginManager()
        Manager_Login.login_view = "auth.login"
        Manager_Login.init_app(app)

        @Manager_Login.user_loader
        def user_load(id):
            return Users.query.get(id)


    # Register blueprints
    app.register_blueprint(init_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)

