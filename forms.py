from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, RadioField, DateField, FloatField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length


class CreateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])

class EditUserForm(FlaskForm):
    username = StringField("Username", render_kw={"disabled": True})
    email = StringField('Email', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Current Password(required)', validators=[DataRequired(), Length(min=8, max=20)])
    new_password = PasswordField('New Password')
    pw_confirm = PasswordField("Confirm New Password")

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])

class CreateTripForm(FlaskForm):
    start_date = DateField("From", validators=[DataRequired()])
    end_date = DateField("To", validators=[DataRequired()])

class AddToDayForm(FlaskForm):
    select_day = SelectField("Select Day", validators=[DataRequired()])

class RemoveButton(FlaskForm):
     pass