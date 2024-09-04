from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, DateField, SubmitField, HiddenField
from wtforms.validators import DataRequired, NumberRange, ValidationError

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


