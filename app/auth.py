from flask import Blueprint, flash, render_template, request, url_for, redirect, session
from .forms import SignUp, Login
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
        return render_template("main_home.html")

@auth_bp.route('/guest')
def guest_home():
    return render_template("main_home.html")  # If not logged in, show main home ska my cover page

from flask_login import login_user
from . import db
from .models import User

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in successfully', category='success')
                return redirect(url_for('auth.home')) # sent to user_home
            else:
                flash('Incorrect password, please try again.', category='error')
        else:
            flash('Email does not exist, please try again.', category='error')
    return render_template('login.html', form = form) # sent to login page

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SignUp()

    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            email = form.email.data.lower()
            password = form.password.data
            hashed_password = generate_password_hash(password)
            user = User(name=name, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash("Your account has been created!", "success")
            return redirect(url_for('auth.login')) # sent to login page
        else:
            flash("Form validation failed. Please check your input.", "error")
    return render_template("signup.html", form=form) # signup was unsuccessful


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', category='success')
    session.modified = True
    return redirect(url_for('auth.home'))