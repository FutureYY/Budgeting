from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, date
from .forms import SpendingForm, SignUp, Login, IncomeForm, ExpensesForm
from app.config import Config
from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


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

@init_bp.route('/')
def home_auth():
    if current_user.is_active:
        return redirect((url_for("#")))
    return render_template("home_page.html")

@init_bp.route('/signup', methods=['GET','POST'])
def signup_auth():
    if current_user.is_active:
        return redirect(url_for("#"))

    form = SignUp(request.form)
    if form.validate_on_submit():
        name = form.name.data.strip()
        new_user = User(name=name, email=form.email.data.lower(), password=generate_password_hash(form.password.date))
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', category='success')
        return render_template("#", form=form)

    return render_template("signup.html", form=form)

@init_bp.route('/login', methods=['GET','POST'])
def login_auth():
    if current_user.us_active:
        return redirect(url_for("#"))

    form = Login(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.lower()).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.show_expenses'))

            else:
                flash('Incorrect password, please try again.', category='error')
        else:
            flash('No account with that email address.', category='error')

    return render_template('login.html', form=form)

@init_bp.route('/logout')
@login_required
def logout_auth():
    logout_user()
    return redirect(url_for('#'))


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

@init_bp.route('/goal', methods=['GET', 'POST'])
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

    expenses_now = db.session.query(db.func.sum(Expense.amount))
    income_now = db.session.query(db.func.sum(Income.amount))
    savings_now = expenses_now

    return render_template('GoalHome.html', selected_section=selected_section, amount=amount)

@init_bp.route('/income', methods=['GET', 'POST'])
def income():
    form = IncomeForm()
    if form.validate_on_submit():
        allowance = form.amount_from_allowance.data
        salary = form.amount_from_salary.data
        angpao = form.amount_from_angpao.data

        # Handle custom incomes
        custom_income = []
        for custom_income in form.custom_income:
            income_type = custom_income.income_type.data
            amount = custom_income.amount.data
            if income_type and amount:
                custom_income.append({'income_type': income_type, 'amount': amount})

        income_to_add = []
        user_id = 1

        if allowance:
            income_to_add.append(Income(user_id=user_id, category='Allowance', amount=allowance))
        if salary:
            income_to_add.append(Income(user_id=user_id, category='Salary', amount=salary))
        if angpao:
            income_to_add.append(Income(user_id=user_id, category='Angpao', amount=angpao))

        #Handle custom Income
        for custom in custom_income:
            income_to_add.append(Income(category=custom['income_type'], amount=custom['amount']))

        # Add all income to the session
        for income in income_to_add:
            db.session.add(income)

        try:
            db.session.commit()
            flash('Income added successfully!', 'success')
        except Exception as e:
            db.session.rollback()  # Rollback if there is an error
            flash(f'An error occurred: {str(e)}', 'danger')

            # Fetch all expenses for the current user
        income_data = Income.query.filter_by(user_id=user_id).all()
        return render_template('GoalHome.html', form=form, income_data=income_data)

            # Fetch all expenses for the current user if the form is not submitted
    user_id = 1  # Adjust this as needed
    income_data = Income.query.filter_by(user_id=user_id).all()
    return render_template('income.html', form=form, income_data=income_data)
@init_bp.route('/savings')
def savings():
    return render_template("savings.html")

@init_bp.route('/goalsetting' , methods=['GET', 'POST'])
def goalsetting():
    form = ExpensesForm()

    if form.validate_on_submit():

        salary = form.salary_expense.data
        allowance = form.allowance_expense.data
        transport = form.transport_expense.data
        entertainment = form.entertainment_expense.data
        technology = form.technology_expense.data
        medical = form.medical_expense.data
        food_beverages = form.food_beverages_expense.data
        books = form.books_expense.data
        stationary = form.stationary_expense.data
        gifts = form.gifts_expense.data
        pets = form.pets_expense.data

        custom_expenses = []
        for custom_expense in form.custom_expenses:
            expenses_type = custom_expense.expenses_type.data
            amount = custom_expense.amount.data
            if expenses_type and amount:
                custom_expenses.append({'expenses_type': expenses_type, 'amount': amount})

        # Handle predefined expenses
        expenses_to_add = []
        user_id = 1

        if transport:
            expenses_to_add.append(Expense(user_id=user_id, category='Transport', amount=transport))
        if entertainment:
            expenses_to_add.append(Expense(user_id=user_id, category='Entertainment', amount=entertainment))
        if technology:
            expenses_to_add.append(Expense(user_id=user_id, category='Technology', amount=technology))
        if medical:
            expenses_to_add.append(Expense(user_id=user_id, category='Medical', amount=medical))
        if food_beverages:
            expenses_to_add.append(Expense(user_id=user_id, category='Food & Beverages', amount=food_beverages))
        if books:
            expenses_to_add.append(Expense(user_id=user_id, category='Books', amount=books))
        if stationary:
            expenses_to_add.append(Expense(user_id=user_id, category='Stationary', amount=stationary))
        if gifts:
            expenses_to_add.append(Expense(user_id=user_id, category='Gifts', amount=gifts))
        if pets:
            expenses_to_add.append(Expense(user_id=user_id, category='Pets', amount=pets))

        #Handle custom expenses
        for custom in custom_expenses:
            expenses_to_add.append(Expense(category=custom['expenses_type'], amount=custom['amount']))

        # Add all expenses to the session
        for expense in expenses_to_add:
            db.session.add(expense)

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



@init_bp.errorhandler(404)
def not_found(error):
    return "This page was not found!", 404


@init_bp.errorhandler(500)
def internal_error(error):
    return "Internal server error!", 500


from .models import Income, Expense, Budget, Transaction, User
