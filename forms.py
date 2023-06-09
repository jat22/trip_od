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
    name = StringField("Trip Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    start_date = DateField("First Day")
    end_date = DateField("Last Day")
    
class UpdateUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    
class LocationSearchForm(FlaskForm):
    loc_type = RadioField(choices=["City/State", "Latitude/Longitude"])
    city = StringField("City")
    state = SelectField("State", choices=
                        ["Alabama","Alaska","Arizona","Arkansas","California","Colorado", "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"])
    lat = StringField("Latitude")
    long = StringField("Longitude")
    radius = IntegerField("Radius")

class DescriptionUpdateForm(FlaskForm):
    description = TextAreaField()

class TripUpdateForm(FlaskForm):
    name = StringField("Trip Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    start_date = DateField("First Day")
    end_date = DateField("Last Day")