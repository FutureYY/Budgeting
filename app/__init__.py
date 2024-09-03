from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from datetime import datetime
from .forms import SpendingForm
from app.config import Config

db = SQLAlchemy()
csrf = CSRFProtect()

init_bp = Blueprint('init', __name__)

@init_bp.route('/tracker', methods=['GET', 'POST'])
def Expenditure_Tracking():
    form = SpendingForm()

    if form.validate_on_submit():
        category = form.category.data
        amount = form.amount.data
        date = form.date.data

        if category in ['entertainment', 'food', 'travel', 'other-expense']:
            expense = Expense(category=category, amount=float(amount), date=datetime.strptime(date, '%Y-%m-%d'))
            db.session.add(expense)
        else:
            income = Income(category=category, amount=float(amount), date=datetime.strptime(date, '%Y-%m-%d'))
            db.session.add(income)

        db.session.commit()
        flash("Spending recorded successfully!")
        return redirect(url_for('init.Expenditure_Tracking'))

    incomes = Income.query.all()
    expenses = Expense.query.all()
    savings_goal = SavingsGoal.query.order_by(SavingsGoal.date.desc()).first()

    total_income = sum([income.amount for income in incomes]) if incomes else 0
    total_expenses = sum([expense.amount for expense in expenses]) if expenses else 0
    savings_goal_amount = savings_goal.amount if savings_goal else 0

    return render_template('FTest1.html', form=form, total_income=total_income, total_expenses=total_expenses,
                           savings_goal=savings_goal_amount)


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

@init_bp.route('/')
def index():
    return render_template('index.html')  # Ensure 'index.html' is in the 'templates' folder

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

@init_bp.errorhandler(404)
def not_found(error):
    return "This page was not found!", 404

@init_bp.errorhandler(500)
def internal_error(error):
    return "Internal server error!", 500

from app.models import Income, Expense, SavingsGoal  # Import models here
