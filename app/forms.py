from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, FloatField, HiddenField, PasswordField
from wtforms.fields import EmailField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
import re

