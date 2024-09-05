from flask import Blueprint, flash, render_template, request, url_for, redirect
from . import db
from .models import User
from .forms import SignUp, Login
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return render_template("user_home.html")

@auth_bp.route('/go_home')
def go_home():
    return render_template("main_home.html")

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    form = Login()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                flash('Logged in successfully', category='success')
                return redirect(url_for('auth.home'))
            else:
                flash('Incorrect password, please try again.', category='error')
        else:
            flash('No account with that email address.', category='error')

    return render_template("login.html", form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SignUp()

    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data
            password = form.password.data
            hashed_password = generate_password_hash(password)
            user = User(name=name, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash("Your account has been created!", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Form validation failed. Please check your input.", "error")
    return render_template("signup.html", form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.go_home'))