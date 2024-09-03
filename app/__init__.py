from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from .forms import SpendingForm
from app.config import Config

db = SQLAlchemy()
csrf = CSRFProtect()

init_bp = Blueprint('init', __name__)


# for yoshana's home route - thank you :)
@init_bp.route('/')
def home():
    return render_template("home_page.html")


@init_bp.route('/Login_page')
def login():
    return render_template("Login_page.html")


@init_bp.route('/Signup_page')
def signup():
    return render_template("Signup_page.html")


@init_bp.route('/tracker', methods=['GET', 'POST'])
def Expenditure_Tracking():
    form = SpendingForm()

    if form.validate_on_submit():
        category = form.category.data
        amount = form.amount.data
        date = form.date.data

        transaction_type = 'expense' if category in ['entertainment', 'food', 'travel', 'other-expense'] else 'income'
        transaction = Transaction(
            category=category,
            amount=float(amount),
            date=datetime.strptime(date, '%Y-%m-%d'),
            type=transaction_type,
            user_id=1  # Assume logged in user ID is 1 for this example
        )
        db.session.add(transaction)
        db.session.commit()
        flash("Spending recorded successfully!")
        return redirect(url_for('init.Expenditure_Tracking'))

    # Fetch goals for the current month
    current_date = datetime.now()
    current_month = current_date.strftime('%Y-%m')
    budget = Budget.query.filter_by(user_id=1, month=current_month).first()

    if budget:
        income_goal = budget.income_goal
        expense_goal = budget.expense_goal
        savings_goal = budget.savings_goal
    else:
        income_goal = expense_goal = savings_goal = 0

    # Calculate current income and expenses for the month
    current_income = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=1, type='income').filter(db.func.strftime('%Y-%m', Transaction.date) == current_month).scalar() or 0

    current_expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        user_id=1, type='expense').filter(db.func.strftime('%Y-%m', Transaction.date) == current_month).scalar() or 0

    remaining_savings = savings_goal - current_expenses if savings_goal else 0

    return render_template('FTest1.html', form=form, income_goal=income_goal, expense_goal=expense_goal,
                           savings_goal=savings_goal, current_income=current_income,
                           current_expenses=current_expenses, remaining_savings=remaining_savings)

@init_bp.route('/get_overview/<month>', methods=['GET'])
def get_overview(month):
    # Assume user_id = 1 for simplicity
    user_id = 1

    # Fetch budget for the selected month
    budget = Budget.query.filter_by(user_id=user_id, month=month).first()
    if budget:
        income_goal = budget.income_goal
        expense_goal = budget.expense_goal
        savings_goal = budget.savings_goal
    else:
        income_goal = expense_goal = savings_goal = 0

    # Calculate current income and expenses for the selected month
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


@init_bp.route('/educate')
def educate():
    return render_template("educate.html")


@init_bp.route('/budget')
def budget():
    return render_template("budget.html")


@init_bp.route('/saving')
def saving():
    return render_template("saving.html")


@init_bp.route('/expenses')
def expenses():
    return render_template("expenses.html")

@init_bp.route('/goal')
def goal(): 
    return render_template("GoalHome.html")

@init_bp.route('/income')
def income():
    return render_template("Income.html")

@init_bp.route('/goalsetting')
def goalsetting():
    return render_template("GoalSetting.html")

@init_bp.errorhandler(404)
def not_found(error):
    return "This page was not found!", 404


@init_bp.errorhandler(500)
def internal_error(error):
    return "Internal server error!", 500


from .models import Income, Expense, Budget, Transaction
