from os import path
from datetime import date
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from app.auth import auth_bp
from app.config import Config
from app.models import db
from flask_login import LoginManager
from app.models import User,Budget,Transaction,Income,Expense
from app import init_bp

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='app/static')
    app.config.from_object(config_class)

    db.init_app(app)
    csrf = CSRFProtect()
    csrf.init_app(app)

    with app.app_context():
        if not path.exists(app.config['DATABASE_NAME']):
            db.create_all()
            print('Created Database!')
            # insert_dummy_data()
<<<<<<< Updated upstream
=======
            # users_check()
>>>>>>> Stashed changes

    from app.models import User

    manager_login = LoginManager()
    manager_login.login_view = "auth.login"
    manager_login.init_app(app)

    @manager_login.user_loader
    def user_load(id):
        return User.query.get(id)

    # Register blueprints for init and authentication(auth)
    app.register_blueprint(init_bp)
    app.register_blueprint(auth_bp)

    return app


<<<<<<< Updated upstream
# def insert_dummy_data():
#     # Check if the user already exists
#     existing_user = User.query.filter_by(email='testuser@example.com').first()
#
#     if not existing_user:
#         user = User(username='testuser', email='testuser@example.com')
#         db.session.add(user)
#         db.session.commit()
#
#
#         budget = Budget(month='2024-09', income_goal=1500.00, savings_goal=500.00, expense_goal=1000.00,
#                         user_id=user.id)
#         db.session.add(budget)
#
#         transaction1 = Transaction(amount=1000.00, category='salary', type='income', date=date.today(), user_id=user.id,
#                                    budget_id=budget.id)
#         transaction2 = Transaction(amount=50.00, category='food_beverages', type='expense', date=date.today(),
#                                    user_id=user.id, budget_id=budget.id)
#         db.session.add_all([transaction1, transaction2])
#
#         db.session.commit()
#         print('Inserted Dummy Data!')
#     else:
#         print('User already exists, skipping dummy data insertion.')
=======
def insert_dummy_data():
    # Check if the user already exists
    existing_user = User.query.filter_by(email='testuser@example.com').first()

    if not existing_user:
        user = User(name='testuser', email='testuser@example.com')
        db.session.add(user)
        db.session.commit()

        income1 = Income(amount=1000.00, category='salary', user_id=user.id)
        income2 = Income(amount=200.00, category='allowance', user_id=user.id)
        db.session.add_all([income1, income2])

        expense1 = Expense(amount=50.00, category='food_beverages', user_id=user.id)
        expense2 = Expense(amount=30.00, category='transport', user_id=user.id)
        db.session.add_all([expense1, expense2])

        budget = Budget(month='2024-09', income_goal=1500.00, savings_goal=500.00, expense_goal=1000.00,
                        user_id=user.id)
        db.session.add(budget)

        transaction1 = Transaction(amount=1000.00, category='salary', type='income', date=date.today(), user_id=user.id,
                                   budget_id=budget.id)
        transaction2 = Transaction(amount=50.00, category='food_beverages', type='expense', date=date.today(),
                                   user_id=user.id, budget_id=budget.id)
        db.session.add_all([transaction1, transaction2])

        db.session.commit()
        print('Inserted Dummy Data!')
    else:
        print('User already exists, skipping dummy data insertion.')
>>>>>>> Stashed changes

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)