from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, HiddenField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class SpendingForm(FlaskForm):
    category = SelectField(
        'Category',
        choices=[
            ('entertainment', 'Entertainment'),
            ('food', 'Food'),
            ('travel', 'Travel'),
            ('other-expense', 'Other Expense'),
            ('allowance', 'Allowance'),
            ('salary', 'Salary'),
            ('other-income', 'Other Income')
        ],
        validators=[DataRequired()]
    )
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    date = HiddenField('Date', validators=[DataRequired()])
    submit = SubmitField('Submit')
