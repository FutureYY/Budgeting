from os import path

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from app.config import Config
from app.models import db
from app import init_bp

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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)


# from app import db, Income, Expense, SavingsGoal

# # Dummy incomes
# income1 = Income(category="salary", amount=500, date="2024-08-01")
# income2 = Income(category="allowance", amount=100, date="2024-08-05")
#
# # Dummy expenses
# expense1 = Expense(category="food", amount=200, date="2024-08-10")
# expense2 = Expense(category="entertainment", amount=50, date="2024-08-15")
#
# # Dummy savings goal
# savings_goal = SavingsGoal(amount=250, date="2024-08-01")
#
# # Add all to session
# db.session.add(income1)
# db.session.add(income2)
# db.session.add(expense1)
# db.session.add(expense2)
# db.session.add(savings_goal)
#
# # Commit to the database
# db.session.commit()
#
# flask shell

