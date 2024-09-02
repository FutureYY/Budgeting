from flask import Blueprint, flash, render_template, request, url_for, redirect
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

routes = Blueprint('routes', __name__)