from flask import Flask, redirect, render_template, url_for, request, flash, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import json
from keys import REC_API_KEY, MAPS_KEY, TOMTOM_KEY
from datetime import timedelta, date, datetime
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError


from models import connect_db, db, User, Trip, Location, TripDay, DayActivity, UnassignedTripActivities, UnassignedTripCampground, Link
from forms import CreateAccountForm, CreateTripForm, LoginForm, LocationSearchForm
from functions import search_by_location, get_location_details, make_date_dict, trip_dates

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


####################### CREATES TRIP##############################

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

        
        trip_days = trip_dates(new_trip.start_date, new_trip.end_date)

        for d in trip_days:
            new_day = TripDay(
                trip_id = new_trip.id,
                date = d["datetime"],
                dow = d["dow"],
                year = d["year"],
                month = d["month"],
                day = d["day"]
            )
            db.session.add(new_day)
            db.session.commit()

        # trip_days = []
        # i = new_trip.start_date
        # while i <= new_trip.end_date:
        #     trip_days.append(i)
        #     i += timedelta(days=1)

        # for day in trip_days:
        #     new_day = TripDay(
        #         trip_id = new_trip.id,
        #         date = day
        #     )
        #     db.session.add(new_day)
        #     db.session.commit()

        session[CURR_TRIP] = new_trip.id
        
        return redirect(f"/trips/{new_trip.id}/where")
    
    return render_template("form-simple.html", form=form, title="New Trip", action="/trips/create", submit_button="Create", back_action="/", method="POST")



####################### LOCATION SEARCH INPUT##############
@app.route("/trips/<int:trip_id>/where")
def trip_location(trip_id):
    return render_template("/trip/search.html", trip_id=trip_id)


################### LOCATION SEARCH
@app.route("/api/search")
def search():
    city = request.args.get("city")
    state = request.args.get("state")
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    radius = request.args.get("radius")
    
    results = search_by_location(city, state, latitude, longitude, radius)
    return jsonify(results)




########################CAMPGROUNDS####################

########   Show Campground Results   #########
@app.route("/trips/<int:trip_id>/campgrounds")
def show_campgrounds(trip_id):
    return render_template("/results/campgrounds.html", trip_id=trip_id)

####### Campground Details
@app.route("/campgrounds/<campground_id>")
def show_campground_details(campground_id):
    campground_details = get_location_details(campground_id)
	
    return render_template("/trip/campground-details.html", location=campground_details, session=session)

############# Add Campground to Trip
@app.route("/trips/<int:trip_id>/campgrounds/<location_id>/add", methods=["POST"])
def add_campground(trip_id, location_id):

    if Location.query.get(location_id):
        new_unassinged_cg = UnassignedTripCampground(
            campground = location_id,
            trip = session[CURR_TRIP]
        )
        db.session.add(new_unassinged_cg)
        db.session.commit()
    else:
        cmpgrd_data = get_location_details(location_id)
        links = cmpgrd_data.pop("links")

        new_location = Location(**cmpgrd_data)
        db.session.add(new_location)
        db.session.commit()

        for link in links:
            new_link = Link(**link)
            db.session.add(new_link)
            db.session.commit()

        new_unassinged_cg = UnassignedTripCampground(
            campground = location_id,
            trip = trip_id)
        
        db.session.add(new_unassinged_cg)
        db.session.commit()
    # flash(f"{cmpgrd_data['name']} added to your trip", "success")
    return redirect(f"/trips/{trip_id}/campgrounds")


################### ACTIVITIES ###################

########### Activity Search Results
@app.route("/trips/<int:trip_id>/activities")
def show_activitiy_options(trip_id):
    return render_template("/results/activities.html", trip_id=trip_id)

@app.route("/trips/<int:trip_id>/<activity_name>")
def activity_locations(trip_id, activity_name):
    return render_template("trip/activity-locations.html", trip_id=trip_id, activity_name=activity_name)

############### Activity location page
@app.route("/trips/<int:trip_id>/<activity_name>/<location_id>/add", methods=["POST"])
def add_activity_to_trip(trip_id, activity_name, location_id):
    
    if Location.query.get(location_id):


        new_unassigned_activity = UnassignedTripActivities(
            activity = activity_name,
            location_id = location_id,
            trip = trip_id
        )
        db.session.add(new_unassigned_activity)
        db.session.commit()
    else:
        location_data = get_location_details(location_id)
        links = location_data.pop("links")

        new_location = Location(**location_data)
        db.session.add(new_location)
        db.session.commit()

        for link in links:
            new_link = Link(**link)
            db.session.add(new_link)
            db.session.commit()

        new_unassigned_activity = UnassignedTripActivities(
            activity = activity_name,
            location_id = location_id,
            trip = trip_id
        )
        db.session.add(new_unassigned_activity)
        db.session.commit()

    flash(f"{activity_name} added to your trip", "success")

    return redirect(f"/trips/{trip_id}/activities")


@app.route("/trips/<int:trip_id>")
def show_a_trip(trip_id):
    trip = Trip.query.get(trip_id)
    # dates = [make_date_dict(day.date) for day in trip.days]

    return render_template("/trip/trip-details.html", trip = trip)

@app.route("/trips/<int:trip_id>/campground/assign", methods=["POST"])
def assign_campground(trip_id):
    day_id = request.form.get("camp-day")
    campground_id = request.form.get("location-id")

    trip_day = TripDay.query.get(day_id)

    trip_day.campground_id = campground_id
    db.session.add(trip_day)

    u_campground = UnassignedTripCampground.query.filter(and_(UnassignedTripCampground.campground==campground_id, UnassignedTripCampground.trip==trip_id)).first()
    
    db.session.delete(u_campground)
    db.session.commit()

    return redirect(f"/trips/{trip_id}")