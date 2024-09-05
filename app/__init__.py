from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, date
from .forms import SpendingForm, SignUp, Login, IncomeForm, ExpensesForm, CustomExpensesForm
from app.config import Config
from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask import Flask, render_template, request, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()
csrf = CSRFProtect()

init_bp = Blueprint('init', __name__)

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
    custom_expenses = Expense.query.filter_by(user_id=user_id).filter(
        Expense.category == 'other-expense',
        Expense.custom_category != None  # This checks if custom_category is NOT NULL
    ).all()

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

    if income_now == 0 and expenses_now !=0:
        savings_now = - expenses_now
    elif income_now!=0 and expenses_now == 0:
        savings_now = income_now
    else:
        savings_now = income_now - expenses_now if income_now and expenses_now else 0

    income_data = Income.query.filter_by(user_id=user_id).all()
    expenses_data = Expense.query.filter_by(user_id=user_id).all()

    return render_template('GoalHome.html', selected_section=selected_section, amount=amount, income_data=income_data, expenses_data=expenses_data, savings_now=savings_now, expenses_now=expenses_now, income_now=income_now)

@init_bp.route('/income', methods=['GET', 'POST'])
def income():
    form = IncomeForm()

    if form.validate_on_submit():
        # User ID (replace with actual user ID)
        user_id = current_user.id

        # Create a list to store entries to be added
        entries_to_add = []

        # Process predefined income categories
        if form.amount_from_allowance.data:
            entries_to_add.append(Income(
                user_id=current_user.id,
                category='Allowance',
                amount=form.amount_from_allowance.data
            ))
        if form.amount_from_salary.data:
            entries_to_add.append(Income(
                user_id=current_user.id,
                category='Salary',
                amount=form.amount_from_salary.data
            ))
        if form.amount_from_angpao.data:
            entries_to_add.append(Income(
                user_id=current_user.id,
                category='Angpao',
                amount=form.amount_from_angpao.data
            ))

        # Process custom income fields
        for i in range(len(form.custom_income)):
            income_type = form.custom_income[i].income_type.data
            amount = form.custom_income[i].amount.data

            if income_type and amount:
                entries_to_add.append(Income(
                    user_id=current_user.id,
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
    user_id = current_user.id  # Replace with actual user ID
    income_data = Income.query.filter_by(user_id=user_id).all()

    return render_template('income.html', form=form, income_data=income_data)



# YENYI'S ROUTES (END)


@init_bp.route('/new_expense', methods=['GET', 'POST'])
def new_expense():
    form = ExpensesForm()

    if form.validate_on_submit():
        # User ID (replace with actual user ID)
        user_id = current_user.id

        # Create a list to store entries to be added
        entries_to_add = []

        # Process predefined expense categories
        if form.transport_expense.data:entries_to_add.append(Expense( user_id=current_user.id ,category='Transport', amount=form.transport_expense.data ))
        if form.entertainment_expense.data: entries_to_add.append(Expense(user_id=current_user.id , category='Entertainment', amount=form.entertainment_expense.data))
        if form.technology_expense.data: entries_to_add.append(Expense(user_id=current_user.id , category='Technology', amount=form.technology_expense.data))
        if form.medical_expense.data:entries_to_add.append(Expense( user_id=current_user.id ,category='Medical', amount=form.medical_expense.data ))
        if form.food_beverages_expense.data: entries_to_add.append(Expense(user_id=current_user.id , category='Food & Beverages', amount=form.food_beverages_expense.data))
        if form.books_expense.data: entries_to_add.append(Expense(user_id=current_user.id , category='Books', amount=form.books_expense.data))
        if form.stationary_expense.data:entries_to_add.append(Expense( user_id=current_user.id ,category='Stationary', amount=form.stationary_expense.data ))
        if form.gifts_expense.data: entries_to_add.append(Expense(user_id=current_user.id , category='Gifts', amount=form.gifts_expense.data))
        if form.pets_expense.data: entries_to_add.append(Expense(user_id=current_user.id , category='Pets', amount=form.pets_expense.data))

        for i in range(len(form.custom_expenses)):
            expense_type = form.custom_expenses[i].expense_type.data
            amount = form.custom_expenses[i].amount.data

            if expense_type and amount:
                entries_to_add.append(Expense(
                    user_id=current_user.id,
                    category='Others',
                    custom_category=expense_type,
                    amount=amount
                ))

        # Save all expense entries to the database
        try:
            for entry in entries_to_add:
                db.session.add(entry)
            db.session.commit()
            flash('Expense added successfully!', 'success')
            return redirect(url_for('init.goal'))  # Redirect after successful submission
        except Exception as e:
            db.session.rollback()  # Rollback if something goes wrong
            flash(f'An error occurred: {str(e)}', 'danger')

    # Fetch all expenses for the current user
    user_id = current_user.id  # Replace with actual user ID
    expense_data = Expense.query.filter_by(user_id=user_id).all()
    return render_template('new_expense.html', form=form, expense_data=expense_data)


# CHRISTEL'S ROUTES (START)

@init_bp.route('/forum')
def forum():
    return render_template("forum.html")


# CHRISTEL'S ROUTES (END)
@init_bp.route('/comments')
def comments():
    return render_template("comments.html")


app = Flask(__name__)

# In-memory list to store comments (for simplicity)
comments_list = []


# Route to display the comments page
@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'POST':
        # Get the comment from the form data
        new_comment = request.form.get('comment')
        if new_comment:
            comments_list.append(new_comment)  # Add comment to the list
        return redirect('/comments')  # Redirect to prevent form resubmission

    # Send the comments list to the HTML template
    return render_template('comments.html', comments=comments_list)


if __name__ == '__main__':
    app.run(debug=True)


@init_bp.errorhandler(404)
def not_found(error):
    return "This page was not found!", 404


@init_bp.errorhandler(500)
def internal_error(error):
    return "Internal server error!", 500


from .models import Income, Expense, Budget, Transaction, User
