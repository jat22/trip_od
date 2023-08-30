from flask import Flask, redirect, render_template, request, flash, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from states import state_names, state_codes
from find import Find
from models import bcrypt, connect_db, db, Trip, User, Park, Campground, ThingToDo, DayThingsToDo, SavedCampground, SavedThingToDo, TripDay
from forms import CreateAccountForm, CreateTripForm, LoginForm, EditUserForm, DescriptionUpdateForm, TripUpdateForm
from keys import NPS_KEY
import urls
import templates

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///rec_trips"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SECRET_KEY'] = "secrets"

debug = DebugToolbarExtension(app)

connect_db(app)

CURR_USER = "curr_user"
CURR_PARK = "curr_park"

def do_login(user):
    """add user to session"""

    session[CURR_USER] = user.username

def do_logout():
    """remove user from session"""

    if CURR_USER in session:
        del session[CURR_USER]

@app.before_request
def add_user_to_g():
    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])
    else:
        g.user = None
        
@app.context_processor
def inject_urls():
    return dict(urls=urls)

@app.context_processor
def inject_user():
    return dict(user=g.user)

################## LANDING PAGE ##########################
@app.route("/")
def show_home():
    """show home page"""

    # state_names = list(state_names.keys())

    return render_template("landing.html", state_names=state_names)

################### USER VIEW FUNCTIONS #############################

@app.route("/users/login", methods=["GET", "POST"])
def login():
    """Show login page and login user"""

    form = LoginForm()

    if form.validate_on_submit():
        print("form validated")
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            return redirect('/')
        flash("Username/Password incorrect", "danger")
    return render_template("users/login.html", form=form)

@app.route("/users/logout")
def logout():
    """Logout current user"""

    do_logout()
    flash("You are now logged out.", "success")
    return redirect("/")

@app.route("/users/new", methods=["GET", "POST"])
def signup():
    """create a mew user account"""

    form = CreateAccountForm()
    
    if form.validate_on_submit():
        username = form.username.data
        try:
            user = User.signup(
                username = username,
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                email = form.email.data,
                password = form.password.data
            )
            db.session.commit()
            

        except IntegrityError:
            flash("Username or Email is already being used", "danger")
            return render_template(templates.users_new, form=form)
        
        do_login(User.query.get(username))
        return redirect(f"users/{username}/trips")
    
    else:
        return render_template("users/new.html", form = form)

@app.route("/users/<username>/profile", methods=["GET", "POST"])
def user_update(username):
    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/users/login")
    
    form = EditUserForm(obj=g.user)
    
    db.session.rollback()
    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            g.user.email = form.email.data
            g.user.first_name = form.first_name.data
            g.user.last_name = form.last_name.data
        else:
            flash("Incorrect Password", "danger")
            return redirect(f"/users/{g.user.username}/profile")
        if form.new_password.data:
            if form.new_password.data == form.pw_confirm.data:
                g.user.password = bcrypt.generate_password_hash(form.new_password.data).decode('UTF-8')
            else:
                flash("New Password does not match", "danger")
                return redirect(f"users/{g.user.username}/profile")
        db.session.commit()
        return redirect(f"/users/{g.user.username}/profile")
    return render_template("users/profile.html", form=form)


######################### SEARCH VIEW #########################
@app.route("/search")
def search_by_state():
    state = request.args.get("state")
    term = request.args.get("term")
    
    results = None
    
    if state and term:
        results = Find.parks(state, term)
    elif state and not term:
        results = Find.parks_by_state(state)
    elif term and not state:
        results = Find.parks_by_term(term)
    

    return render_template("search/results.html", results=results, state_codes=state_codes, state_names=state_names, search={"state":state, "term":term})

@app.route("/parks/<park_code>")
def park_details(park_code):

    park_details = Find.park_details(park_code)
    session[CURR_PARK] = park_code

    return render_template("search/parkDetails.html", details=park_details)


##################### TRIP VIEW FUNCTIONS ##############################

@app.route("/users/<username>/trips/new", methods=["GET", "POST"])
def new_trip(username):

	form = CreateTripForm()
        
	if form.validate_on_submit():
		new_trip = Trip.create(
			start_date = form.start_date.data,
			end_date = form.end_date.data,
			notes = form.notes.data,
			username = g.user.username,
			park_code = session[CURR_PARK]
		)

		return redirect(f"/users/{g.user.username}/trips/{new_trip.id}")
        
	return render_template("trips/new.html", park = session[CURR_PARK], form=form)

@app.route("/users/<username>/trips/<trip_id>")
def trip_details(username, trip_id):
	trip = Trip.query.get(trip_id)
	days = TripDay.query.filter(TripDay.trip_id==trip_id).order_by(TripDay.date).all()

	return render_template("trips/details.html", trip=trip, days=days)

@app.route("/users/<username>/trips")
def user_trips(username):
    
	return render_template("users/tripList.html")


@app.route("/trips/<trip_id>/things/<thing_id>/add", methods=["POST"])
def add_thing(trip_id, thing_id):
	day_id = request.form.get("day")
	DayThingsToDo.create(
		day_id = day_id,
		trip_id = trip_id,
		thing_id = thing_id
	)

	return redirect(f"/users/{g.user.username}/trips/{trip_id}")

@app.route("/trips/<trip_id>/campgrounds/<campground_id>/add", methods=["POST"])
def add_campground(trip_id, campground_id):
	day_id = request.form.get("day")
	TripDay.add_campground(day_id, campground_id)

	return redirect(f"/users/{g.user.username}/trips/{trip_id}")

@app.route("/trips/<trip_id>/days/<day_id>/thing/<thing_id>/remove", methods=["POST"])
def remove_thing(trip_id, day_id, thing_id):
	DayThingsToDo.remove(day_id, thing_id)
	
	return redirect(f"/users/{g.user.username}/trips/{trip_id}")

@app.route("/trips/<trip_id>/days/<day_id>/campground/remove", methods=["POST"])
def remove_campground(trip_id, day_id):
	TripDay.remove_campground(day_id)
	
	return redirect(f"/users/{g.user.username}/trips/{trip_id}")

@app.route("/trips/<trip_id>/delete", methods=["POST"])
def delete_trip(trip_id):
	Trip.delete(trip_id)

	return redirect(f"/users/<username>/trips")