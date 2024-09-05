from flask import Blueprint, flash, render_template, request, url_for, redirect
from . import db
from .models import User
from .forms import SignUp, Login
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    if current_user.is_active:
        return redirect(url_for("user_home.html"))
    return render_template("main_home.html")

@auth_bp.route('/signup', methods=['GET','POST'])
def signup():
    if current_user.is_active:
        return redirect(url_for("user_home.html"))

    form = SignUp(request.form)
    if form.validate_on_submit():
        name = form.name.data.strip()
        new_user = User(name=name, email=form.email.data.lower(), password=generate_password_hash(form.password.date))
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', category='success')
        return render_template("auth.login", form=form)

    return render_template("signup.html", form=form)

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_active:
        return redirect(url_for("user_home.html"))

    form = Login(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.lower()).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('user_home.html'))

            else:
                flash('Incorrect password, please try again.', category='error')
        else:
            flash('No account with that email address.', category='error')

    return render_template("login.html", form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))