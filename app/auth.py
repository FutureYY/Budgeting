from flask import Blueprint, flash, render_template, request, url_for, redirect
from werkzeug.security import generate_password_hash
from . import db
from .models import Users
from .forms import SignUp, Login
from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)


auth.route('/')
def home():
    if current_user.is_active:
        return redirect((url_for("#")))
    return render_template("home_page.html")

@auth.route('/signup', methods=['GET','POST'])
def signup():
    if current_user.is_active:
        return redirect(url_for("#"))
        form = SignUp(request.form)
        if form.validate_on_submit():
            name = form,name.data.strip()
            new_user = Users(name=name, email=form.email.data.lower(), password=generate_password_hash(form.password.date))
            db.session.add(new_user)
            db.session.commit()

            flash('Account created successfully!', category='success')

        return render_template("signup.html", form=form)

@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.us_active:
        return redirect(url_for("#"))

    form = Login(request.form)
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.lower()).first()
    return render_template('login.html')

@auth.route('/logout')
# @login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))