from os import path
<<<<<<< Updated upstream
from datetime import date
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from app.config import Config
from app.models import db
from flask_login import LoginManager
from app.models import User,Budget,Transaction,Income,Expense

from app import init_bp
=======

from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from app.config import Config
from app.models import db, User
# from app import init_bp
from flask_login import LoginManager
from app.forms import LoginIn
>>>>>>> Stashed changes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf = CSRFProtect()
    # csrf.init_app(app)

    with app.app_context():
        if not path.exists(app.config['DATABASE_NAME']):
            db.create_all()
            print('Created Database!')
<<<<<<< Updated upstream
            insert_dummy_data()
=======
        csrf.init_app(app)

        manager_login = LoginManager()
        manager_login.login_view = "init.login_auth"
        manager_login.init_app(app)
>>>>>>> Stashed changes

        @manager_login.user_loader
        def user_load(id):
            return User.query.get(id)

        from app import init_bp

        # Register blueprints
        app.register_blueprint(init_bp)



    # @app.route('/login', methods=['GET', 'POST'])
    # def login():
    #     form = LoginIn()  # Initialize your form
    #     if form.validate_on_submit():
    #         # Handle form submission
    #         pass
    #     return render_template("Login_page.html", form=form)  # Pass the form to the template

    # Register blueprints
    app.register_blueprint(init_bp)

    return app


def insert_dummy_data():
    # Check if the user already exists
    existing_user = User.query.filter_by(email='testuser@example.com').first()

    if not existing_user:
        user = User(username='testuser', email='testuser@example.com')
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


if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)