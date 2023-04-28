from flask import Flask, redirect, render_template, url_for, request, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
import json
from keys import REC_API_KEY, MAPS_KEY, TOMTOM_KEY

from sqlalchemy.exc import IntegrityError

from models import connect_db, db, User, Trip, Location, Activity, TripDay, DayActivity, Campground, UnassignedTripActivities, UnassignedTripCampground
from forms import CreateAccountForm, CreateTripForm, LoginForm, LocationSearchForm

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///rec_trips'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "secrets"

debug = DebugToolbarExtension(app)

connect_db(app)

db.create_all()

CURR_USER = "curr_user"
CURR_TRIP = "curr_trip"
REC_BASE_URL = "https://ridb.recreation.gov/api/v1"
GEOCODE_BASE_URL = "https://api.tomtom.com/search/2/geocode/"

def do_login(user):
    session[CURR_USER] = user.username

def do_logout():
    if CURR_USER in session:
        del session[CURR_USER]

@app.before_request
def add_user_to_g():
    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])
    else:
        g.user = None

@app.route("/")
def show_home():
    return render_template("home.html")


################### USER VIEW FUNCTIONS #############################

@app.route("/users/new", methods=["GET", "POST"])
def signup():
    form = CreateAccountForm()
    
    if form.validate_on_submit():
        try:
            user = User.signup(
                username = form.username.data,
                email = form.email.data,
                password = form.password.data
            )
            db.session.commit()
        except IntegrityError:
            flash("Username is already taken", "danger")
            return render_template("/users/user-new.html", form=form)
        
        return redirect(f"/users/{form.username.data}")
    
    else:
        return render_template("/users/user-new.html", form = form)

@app.route("/users/<username>")
def user_profile(username):
    user = User.query.get(username)
    return render_template("users/user-profile.html", user=user)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            return redirect('/')
        flash("Password/User incorrect", "danger")
    return render_template('form-simple.html', form=form, title=login, action="/login", submit_button = "Login", back_action="/", method="POST")

@app.route('/logout')
def logout():
    do_logout()
    flash("You are now logged out.", "success")
    return redirect('/')


####################### TRIP VIEW FUNCTIONS ##############################

@app.route("/trips/create", methods=["GET", "POST"])
def create_trip():
    form = CreateTripForm()
    
    if form.validate_on_submit():
        if not g.user:
            flash("Please Login or Create an Account")
            return redirect("/login")
        new_trip = Trip(
            name = form.name.data,
            start_date = form.start_date.data,
            end_date = form.end_date.data,
            description = form.description.data,
            user = g.user.username
		)
        db.session.add(new_trip)
        db.session.commit()
        
        session[CURR_TRIP] = new_trip.id
        
        return redirect(f"/trips/where")
    
    return render_template("form-simple.html", form=form, title="New Trip", action="/trips/create", submit_button="Create", back_action="/", method="POST")

@app.route("/trips/where")
def trip_location():
    form = LocationSearchForm()
    if form.validate_on_submit():
        city = form.city.data
        state = form.state.data
        lat = form.lat.data
        long = form.long.data
        
        return redirect("/trips/stay")
    
    return render_template("form-simple.html", form=form, title="Where", action="/trips/where", submit_button="Next", back_action="/", method="GET")