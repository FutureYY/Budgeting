from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, date
from .forms import SpendingForm, SignUp, Login, IncomeForm, ExpensesForm, CustomExpensesForm
from app.config import Config
from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()
csrf = CSRFProtect()

init_bp = Blueprint('init', __name__)

# Yoshana's Routing :)
# @init_bp.route('/')
# def main_home():
#     return render_template("main_home.html")
#
# @init_bp.route('/user')
# def user_home():
#     return render_template("user_home.html")
#
# @init_bp.route('/login')
# def login():
#     return redirect(url_for("auth.login"))
#
# @init_bp.route('/signup')
# def signup():
#     return render_template("signup.html")

#ZAK'S ROUTES START
@init_bp.route('/tracker', methods=['GET', 'POST'])
def Expenditure_Tracking():
    form = SpendingForm()

    #Load dropdown categories based on user and current month
    user_id = 1  # REPLACE WITH SESSION ID
    current_month = date.today().strftime('%Y-%m')
    categories = load_categories(user_id, current_month)
    form.category.choices = categories

    if form.validate_on_submit():
        category = form.category.data
        amount = form.amount.data
        transaction_date = form.date.data

        #determine transaction type
        transaction_type = 'income' if category in ['allowance', 'salary', 'other-income'] else 'expense'

        # Create and save the transaction
        transaction = Transaction(
            category=category,
            amount=float(amount),
            date=datetime.strptime(transaction_date, '%Y-%m-%d'),
            type=transaction_type,
            user_id=user_id  # Replace with actual user ID from session
        )
        db.session.add(transaction)
        db.session.commit()

        flash("Spending recorded successfully!")
        return redirect(url_for('init.Expenditure_Tracking'))

    # Fetch the budget goals for the current month
    current_date = datetime.now()
    current_month = current_date.strftime('%Y-%m')
    budget = Budget.query.filter_by(user_id=user_id, month=current_month).first()

    if budget:
        income_goal = budget.income_goal
        expense_goal = budget.expense_goal
        savings_goal = budget.savings_goal
    else:
        income_goal = expense_goal = savings_goal = 0

    # Calculate current income and expenses for the month
    current_income = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=user_id, type='income').filter(db.func.strftime('%Y-%m', Transaction.date) == current_month).scalar() or 0

    current_expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=user_id, type='expense').filter(db.func.strftime('%Y-%m', Transaction.date) == current_month).scalar() or 0

    remaining_savings = savings_goal - current_expenses if savings_goal else 0

    return render_template('tracking.html', form=form, income_goal=income_goal, expense_goal=expense_goal,
                           savings_goal=savings_goal, current_income=current_income,
                           current_expenses=current_expenses, remaining_savings=remaining_savings)

def load_categories(user_id, month):
    categories = [
        ('salary', 'Salary'),
        ('allowance', 'Allowance'),
        ('other-income', 'Other Income'),
        ('transport', 'Transport'),
        ('entertainment', 'Entertainment'),
        ('technology', 'Technology'),
        ('medical', 'Medical'),
        ('food_beverages', 'Food and Beverages'),
        ('books', 'Books'),
        ('stationary', 'Stationary'),
        ('gifts', 'Gifts'),
        ('pets', 'Pets'),
        ('other-expense', 'Other Expense')
    ]

    #Retrieve custom categories
    custom_income = Income.query.filter_by(user_id=user_id).filter(Income.category=='other-income', Income.custom_category.isnot(None)).all()
    custom_expenses = Expense.query.filter_by(user_id=user_id).filter(Expense.category=='other-expense', Expense.custom_category.isnot(None)).all()

    for income in custom_income:
        categories.append((income.custom_category, income.custom_category))

    for expense in custom_expenses:
        categories.append((expense.custom_category, expense.custom_category))

    return categories

@init_bp.route('/get_overview/<month>', methods=['GET'])
def get_overview(month):
    # CHANGE
    user_id = 1

    # retrieve goals/budget for selected month
    budget = Budget.query.filter_by(user_id=user_id, month=month).first()
    if budget:
        income_goal = budget.income_goal
        expense_goal = budget.expense_goal
        savings_goal = budget.savings_goal
    else:
        income_goal = expense_goal = savings_goal = 0

    # current income and expense for selected month (caluclate)
    current_income = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=user_id, type='income').filter(db.func.strftime('%Y-%m', Transaction.date) == month).scalar() or 0

    current_expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=user_id, type='expense').filter(db.func.strftime('%Y-%m', Transaction.date) == month).scalar() or 0

    remaining_savings = savings_goal - current_expenses if savings_goal else 0

    # Return the data as JSON
    return jsonify({
        'income_goal': float(income_goal),
        'expense_goal': float(expense_goal),
        'savings_goal': float(savings_goal),
        'current_income': float(current_income),
        'current_expenses': float(current_expenses),
        'remaining_savings': float(remaining_savings)
    })

@init_bp.route('/get_transactions/<month>', methods=['GET'])
def get_transactions(month):
    user_id = 1  # Replace with session ID

    # Query for all transactions of the user for the selected month, ordered by date
    transactions = Transaction.query.filter_by(user_id=user_id).filter(
        db.func.strftime('%Y-%m', Transaction.date) == month).order_by(Transaction.date).all()

    # Format the transactions to be returned as JSON
    transactions_data = [
        {
            'date': transaction.date.strftime('%Y-%m-%d'),
            'category': transaction.category,
            'amount': float(transaction.amount)
        }
        for transaction in transactions
    ]

    return jsonify(transactions_data)


@init_bp.route('/get_categories/<month>', methods=['GET'])
def get_categories(month):
    user_id = 1  # Replace with session ID
    categories = load_categories(user_id, month)
    return jsonify(categories)

#ZAK'S ROUTES END


@init_bp.route('/educate')
def educate():
    return render_template("educate.html")


# JIAWEN'S ROUTES (START)

@init_bp.route('/budget')
def budget():
    return render_template("budget.html")


@init_bp.route('/saving')
def saving():
    return render_template("saving.html")


@init_bp.route('/expensescontent')
def expensescontent():
    return render_template("expensescontent.html")

# JIAWEN'S ROUTES (END)


# YENYI'S ROUTES (START)

@init_bp.route('/goal', methods=['GET'])
def goal():
    # if not current_user.is_authenticated:
    #     # Redirect to login page or handle unauthenticated access
    #     return redirect(url_for('init.login'))

    selected_section = None
    amount = None
    user_id = 1

    if request.method == 'POST':
        # Assuming your form has fields 'section' and 'amount'
        selected_section = request.form.get('section')
        amount = request.form.get('amount')

    # current_income = db.session.query(db.func.sum(Income.amount)).filter_by(
    #     user_id=user_id, type='income')

    expenses_now = db.session.query(db.func.sum(Expense.amount)).filter_by(user_id=user_id).scalar() or 0
    income_now = db.session.query(db.func.sum(Income.amount)).filter_by(user_id=user_id).scalar() or 0
    savings_now = income_now - expenses_now if income_now and expenses_now else 0

    income_data = Income.query.filter_by(user_id=user_id).all()
    expenses_data = Expense.query.filter_by(user_id=user_id).all()

    return render_template('GoalHome.html', selected_section=selected_section, amount=amount, income_data=income_data, expenses_data=expenses_data, savings_now=savings_now, expenses_now=expenses_now, income_now=income_now)

@init_bp.route('/income', methods=['GET', 'POST'])
def income():
    form = IncomeForm()

    if form.validate_on_submit():
        # User ID (replace with actual user ID)
        user_id = 1

        # Create a list to store entries to be added
        entries_to_add = []

        # Process predefined income categories
        if form.amount_from_allowance.data:
            entries_to_add.append(Income(
                user_id=user_id,
                category='Allowance',
                amount=form.amount_from_allowance.data
            ))
        if form.amount_from_salary.data:
            entries_to_add.append(Income(
                user_id=user_id,
                category='Salary',
                amount=form.amount_from_salary.data
            ))
        if form.amount_from_angpao.data:
            entries_to_add.append(Income(
                user_id=user_id,
                category='Angpao',
                amount=form.amount_from_angpao.data
            ))

        # Process custom income fields
        for i in range(len(form.custom_income)):
            income_type = form.custom_income[i].income_type.data
            amount = form.custom_income[i].amount.data

            if income_type and amount:
                entries_to_add.append(Income(
                    user_id=user_id,
                    category='Others',
                    custom_category=income_type,
                    amount=amount
                ))

        # Save all income entries to the database
        try:
            for entry in entries_to_add:
                db.session.add(entry)
            db.session.commit()
            flash('Income added successfully!', 'success')
            return redirect(url_for('init.goal'))  # Redirect after successful submission
        except Exception as e:
            db.session.rollback()  # Rollback if something goes wrong
            flash(f'An error occurred: {str(e)}', 'danger')

    # Fetch all incomes for the current user
    user_id = 1  # Replace with actual user ID
    income_data = Income.query.filter_by(user_id=user_id).all()

    return render_template('income.html', form=form, income_data=income_data)

@init_bp.route('/savings')
def savings():
    return render_template("savings.html")

@init_bp.route('/goalsetting' , methods=['GET', 'POST'])
def goalsetting():
    form = ExpensesForm()

    if form.validate_on_submit():

        user_id = 1

        expenses_data = {
        'Transport' : form.transport_expense.data,
        'Entertainment' : form.entertainment_expense.data,
        'Technology' : form.technology_expense.data,
        'Medical' : form.medical_expense.data,
        'Food & beverages' : form.food_beverages_expense.data,
        'Books' : form.books_expense.data,
        'Stationary' : form.stationary_expense.data,
        'Gifts' : form.gifts_expense.data,
        'Pets' : form.pets_expense.data
        }

        for category, amount in expenses_data.items():
            if amount:
                expense = Expense(user_id=user_id, category=category, amount=float(amount))
                db.session.add(expense)

        # Handle custom expenses
        for custom_expense in form.custom_expenses.entries:
            expense_type = custom_expense.expense_type.data
            amount = custom_expense.amount.data
            if expense_type and amount:
                custom_expense = Expense(user_id=user_id, category=expense_type, amount=float(amount))
                db.session.add(custom_expense)

        try:
            db.session.commit()
            flash('Expenses added successfully!', 'success')
        except Exception as e:
            db.session.rollback()  # Rollback if there is an error
            flash(f'An error occurred: {str(e)}', 'danger')

            # Fetch all expenses for the current user
        expenses_data = Expense.query.filter_by(user_id=user_id).all()
        return render_template('GoalHome.html', form=form, expenses_data=expenses_data)

        # Fetch all expenses for the current user if the form is not submitted
    user_id = 1  # Adjust this as needed
    expenses_data = Expense.query.filter_by(user_id=user_id).all()
    return render_template('goalsetting.html', form=form, expenses_data=expenses_data)


# YENYI'S ROUTES (END)


# CHRISTEL'S ROUTES (START)

@init_bp.route('/forum')
def forum():
    return render_template("forum.html")


# CHRISTEL'S ROUTES (END)
@init_bp.route('/comments')
def comments():
    return render_template("comments.html")


@init_bp.errorhandler(404)
def not_found(error):
    return "This page was not found!", 404


@init_bp.errorhandler(500)
def internal_error(error):
    return "Internal server error!", 500


from .models import Income, Expense, Budget, Transaction, User
