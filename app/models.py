from enum import unique

from app import db
from datetime import datetime
from decimal import Decimal
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired



#zak
# Transaction Model: This new model tracks actual spending or income as individual transactions. It differentiates between income and expenses using the type field.
# category: Should match one of the predefined categories or a custom category.
# date: Stores the date when the transaction occurred.
# amount: Represents the transaction amount.
# custom_category: Allows for a user-defined category if "others" is selected.
# budget_id: (Optional) Links a transaction to a specific budget for more detailed reporting.

#yoshana and yy :)
#User: Stores user details and establishes relationships with income and expense entries.
# Income: Tracks income amounts and their categories, with an optional custom category for the "others" option.
# Expense: Similar to Income, but for expenses, with predefined categories and a custom option.
# Budget: Holds monthly goals for income, savings, and expenses.
# Budget Model: Tracks the monthly goals for income, savings, and expenses, unchanged from the previous implementation.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    # def is_active(self):
    #     return True  # Modify this if you have a field to handle account deactivation
    #
    # def get_id(self):
    #     return str(self.id)
    #
    # def is_authenticated(self):
    #     return True
    #
    # def is_anonymous(self):
    #     return False

    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    incomes = db.relationship('Income', backref='user', lazy=True)
    expenses = db.relationship('Expense', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    budgets = db.relationship('Budget', backref='user', lazy=True)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'Salary', 'Allowance', 'Others'
    custom_category = db.Column(db.String(100))  # Used if category is 'Others'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'transport', 'entertainment', etc.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    custom_category = db.relationship('User', back_populates='expenses')

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(7), nullable=False)  # Format: YYYY-MM
    income_goal = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    savings_goal = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    expense_goal = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Should match the category/subcategory in Income/Expense
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    custom_category = db.Column(db.String(100))  # Only used if category is 'others'

    #to link this transaction to a specific budget
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each comment
    content = db.Column(db.Text, nullable=False)  # The actual comment text
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Time of comment creation
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    replies = db.relationship('Reply', backref='comment', lazy=True)  # Link to replies

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each reply
    content = db.Column(db.Text, nullable=False)  # The actual reply text
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Time of reply creation
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



    # class Income(db.Model):
#     __tablename__ = 'incomes'
#     id = db.Column(db.Integer, primary_key=True)
#     category = db.Column(db.String(50), nullable=False)
#     amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
#     date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
#
# class Expense(db.Model):
#     __tablename__ = 'expenses'
#     id = db.Column(db.Integer, primary_key=True)
#     category = db.Column(db.String(50), nullable=False)
#     amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
#     date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
#
# class SavingsGoal(db.Model):
#     __tablename__ = 'savings_goals'
#     id = db.Column(db.Integer, primary_key=True)
#     amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
#     date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

