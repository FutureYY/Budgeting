from os import path

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from app.config import Config
from app.models import db
from app import init_bp
from flask_login import LoginManager

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

    # Register blueprints
    app.register_blueprint(init_bp)

    # from app.models import User

    manager_login = LoginManager()
    manager_login.login_view = "auth.login"
    manager_login.init_app(app)

    @manager_login.user_loader
    def user_load(id):
        return User.query.get(id)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)

