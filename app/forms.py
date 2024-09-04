from flask_wtf import FlaskForm
from pyexpat.errors import messages
from wtforms import SelectField, DecimalField, DateField, SubmitField, HiddenField
from wtforms.fields.simple import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Email, Optional, Length, EqualTo
# from .models import Users
import re

class SpendingForm(FlaskForm):
    category = SelectField(
        'Category',
        choices=[
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
        ],
        validators=[DataRequired(message="Please select a category.")]
    )

    amount = DecimalField(
        'Amount',
        places=2,
        validators=[
            DataRequired(message="Please enter an amount."),
            NumberRange(min=0.01, message="Amount must be greater than zero.")
        ]
    )

    # HiddenField to automatically capture the selected date
    date = HiddenField(
        'Date',
        validators=[DataRequired(message="Please select a date.")]
    )

    submit = SubmitField('Submit')


class Login(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email(message='Invalid Email')])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class SignUp(FlaskForm):
    name = StringField('Email', validators=[Optional(), Length(min=8, max=32)])
    email = EmailField('Email*', validators=[DataRequired(), Email(message='Invalid Email')])
    # phone
    password = PasswordField('Password*', validators=[DataRequired(), Length(min=8, max=24)])
    repeat_password = PasswordField('Confirm Password*', validators=[DataRequired(), EqualTo(fieldname="password", message="Passwords must match")])
    submit = SubmitField('Sign Up')