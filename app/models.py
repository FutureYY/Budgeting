from app import db
from datetime import datetime
from decimal import Decimal

class Income(db.Model):
    __tablename__ = 'incomes'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
