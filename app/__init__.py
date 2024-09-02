from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

db = SQLAlchemy()
csrf = CSRFProtect()

init_bp = Blueprint('init', __name__)

@init_bp.route('/')
def home():
    return "Hello, World!"

@init_bp.route('/tracker')
def Expenditure_Tracking():
    # Fetch data from the database
    incomes = Income.query.all()
    expenses = Expense.query.all()
    savings_goal = SavingsGoal.query.order_by(SavingsGoal.date.desc()).first()

    # Calculate totals
    total_income = sum([income.amount for income in incomes])
    total_expenses = sum([expense.amount for expense in expenses])
    savings_goal_amount = savings_goal.amount if savings_goal else 0

    return render_template('FTest1.html', total_income=total_income, total_expenses=total_expenses, savings_goal=savings_goal_amount)

@init_bp.route('/submit-spending', methods=['POST'])
def submit_spending():
    category = request.form.get('category')
    amount = request.form.get('amount')
    date = request.form.get('date')

    if not category or not amount or not date:
        flash("All fields are required!")
        return redirect(url_for('init.Expenditure_Tracking'))

    # Determine if it's an expense or income based on the category
    if category in ['entertainment', 'food', 'travel', 'other-expense']:
        expense = Expense(category=category, amount=float(amount), date=datetime.strptime(date, '%Y-%m-%d'))
        db.session.add(expense)
    else:
        income = Income(category=category, amount=float(amount), date=datetime.strptime(date, '%Y-%m-%d'))
        db.session.add(income)

    db.session.commit()
    flash("Spending recorded successfully!")
    return redirect(url_for('init.Expenditure_Tracking'))

@init_bp.errorhandler(404)
def not_found(error):
    return "This page was not found!", 404

@init_bp.errorhandler(500)
def internal_error(error):
    return "Internal server error!", 500

from app.models import Income, Expense, SavingsGoal  # Import models here
