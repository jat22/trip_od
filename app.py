from flask import Flask, redirect, render_template, request, flash, session, g
from sqlalchemy.exc import IntegrityError
import config, random


from states import state_names, state_codes
from find import Find
from models import bcrypt, connect_db, db, Trip, User, DayThingsToDo, TripDay
from forms import CreateAccountForm, CreateTripForm, LoginForm, EditUserForm, AddToDayForm, RemoveButton
import urls

app = Flask(__name__)

app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI

app.config['SECRET_KEY'] = config.SECRET_KEY
# app.config['WTF_CSRF_SECRET_KEY'] = config.WTF_CSRF_SECRET_KEY

connect_db(app)

CURR_USER = "curr_user"
CURR_PARK = "curr_park"
LOGIN_REFERRER = "login_refer"

def do_login(user):
    """
    add user to session
    """

    session[CURR_USER] = user.username

def do_logout():
    """
    remove user from session
    """

    if CURR_USER in session:
        del session[CURR_USER]

@app.before_request
def add_user_to_g():
    """
    Check if there is a current user logged in; if so add to g.
    """
    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])
    else:
        g.user = None
        
@app.context_processor
def inject_urls():
    """
    Inject urls so accessible in all templates.
    """
    return dict(urls=urls)

@app.context_processor
def inject_user():
    """
    Inject current user so accessible in all templates.
    """
    return dict(user=g.user)

################## LANDING PAGE ##########################
@app.route("/")
def show_home():
    """
    Renders the home page.

    state_names dict is passed to template.
    """

    return render_template("landing.html", state_names=state_names)

################### USER VIEW FUNCTIONS #############################

@app.route("/users/login", methods=["GET", "POST"])
def login():
    """
    GET: Renders login page.

    POST: 
        If form validates, handles login and redirects to previous page before login.; 
        Otherwise renders login page.
    """
    if g.user:
        return redirect("/")
    
    form = LoginForm()
    
    if form.validate_on_submit():

        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            try:
                next_url = session.pop(LOGIN_REFERRER,None)
            except KeyError:
                next_url = "/"
            return redirect(next_url)
        flash("Username/Password incorrect", "danger")
    
    session[LOGIN_REFERRER] = request.referrer
    return render_template("users/login.html", form=form)

@app.route("/users/logout")
def logout():
    """
    Logout current user and redirect to home page.
    """

    do_logout()
    flash("You are now logged out.", "success")
    return redirect("/")

@app.route("/users/new", methods=["GET", "POST"])
def signup():
    """
    GET: render form to create new account.

    POST: create a new user account and redirect home page.
    """

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
            db.session.rollback()
            flash("Username or Email is already being used", "danger")
            return render_template("/users/new", form=form)
        
        do_login(User.query.get(username))
        return redirect(f"/")
    
    else:
        return render_template("users/new.html", form = form)

@app.route("/users/<username>/profile", methods=["GET", "POST"])
def user_update(username):

    """
    GET: render form to edit user information.

    POST: if form validates, handle update and redirect to user profile.
    """

    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/users/login")
    if g.user.username != username:
        flash("Unauthorized", "danger")
        return redirect("/")
    
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

@app.route("/users/<username>/trips/new", methods=["GET", "POST"])
def new_trip(username):
    """
    GET: renders form to create a new trip.

    POST: on form validation, handles creation of new trip; redirects to new trip's detail page.
    """
    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/users/login")
    if g.user.username != username:
        flash("Unauthorized", "danger")
        return redirect("/")

    form = CreateTripForm()
        
    if form.validate_on_submit():
        new_trip = Trip.create(
            start_date = form.start_date.data,
            end_date = form.end_date.data,
            username = g.user.username,
            park_code = session[CURR_PARK]
        )

        return redirect(f"/users/{g.user.username}/trips/{new_trip.id}")
        
    return render_template("trips/new.html", park = session[CURR_PARK], form=form)

@app.route("/users/<username>/trips/<trip_id>")
def trip_details(username, trip_id):
    """
        Renders details for a particulary trip.
    """

    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/users/login")
    if g.user.username != username:
        flash("Unauthorized", "danger")
        return redirect("/")

    trip = Trip.query.get(trip_id)
    days = TripDay.query.filter(TripDay.trip_id==trip_id).order_by(TripDay.date).all()

    form = AddToDayForm()
    remove = RemoveButton()

    form.select_day.choices = [('', 'Select Day')] + [(day.id, f"{day.dow}, {day.month} {day.day}") for day in days]

    return render_template("trips/details.html", trip=trip, days=days, form=form, remove=remove)

@app.route("/users/<username>/trips")
def user_trips(username):
    """
    Renders list of a user's planned trips.
    """

    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/users/login")
    if g.user.username != username:
        flash("Unauthorized", "danger")
        return redirect("/")


    return render_template("users/tripList.html")



######################### SEARCH VIEWS #########################
@app.route("/search")
def search_by_state():
    """
    Handles search based on state and/or term from user input.
    Renders search results.
    """

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

    """
    Renders details for a specific park.
    """

    park_details = Find.park_details(park_code)
    session[CURR_PARK] = park_code

    return render_template("search/parkDetails.html", details=park_details)




##################### TRIP EDIT FUNCTIONS ##############################

@app.route("/trips/<trip_id>/things/<thing_id>/add", methods=["POST"])
def add_thing(trip_id, thing_id):
    """
    Adds a thing_to_do to a trip;
    redirects to current trip's details
    """
    form = AddToDayForm()
    days = TripDay.query.filter(TripDay.trip_id==trip_id).order_by(TripDay.date).all()
    form.select_day.choices = [('', 'Select Day')] + [(day.id, f"{day.dow}, {day.month} {day.day}") for day in days]

    if form.validate_on_submit():
        day_id = form.select_day.data
        DayThingsToDo.create(day_id = day_id,
                            trip_id = trip_id,
                            thing_id = thing_id
        )

    return redirect(f"/users/{g.user.username}/trips/{trip_id}")

@app.route("/trips/<trip_id>/campgrounds/<campground_id>/add", methods=["POST"])
def add_campground(trip_id, campground_id):
    """
    Handles adding a campground to a particular day of the trip.
    Redirects back to trip details.
    """

    form = AddToDayForm()
    days = TripDay.query.filter(TripDay.trip_id==trip_id).order_by(TripDay.date).all()
    form.select_day.choices = [('', 'Select Day')] + [(day.id, f"{day.dow}, {day.month} {day.day}") for day in days]

    if form.validate_on_submit():
        day_id = form.select_day.data
        TripDay.add_campground(day_id, campground_id)

    return redirect(f"/users/{g.user.username}/trips/{trip_id}")

@app.route("/trips/<trip_id>/days/<day_id>/thing/<thing_id>/remove", methods=["POST"])
def remove_thing(trip_id, day_id, thing_id):
    """
    Handles removing a thing_to_do from a day.
    Redirects back to trip details.
    """
    remove = RemoveButton()
    if remove.validate_on_submit():
        DayThingsToDo.remove(day_id, thing_id)

    return redirect(f"/users/{g.user.username}/trips/{trip_id}")

@app.route("/trips/<trip_id>/days/<day_id>/campground/remove", methods=["POST"])
def remove_campground(trip_id, day_id):
    """
    Handles removing a campground from a day.
    Redirects back to trip details.
    """
    remove = RemoveButton()

    if remove.validate_on_submit():
        TripDay.remove_campground(day_id)
	
    return redirect(f"/users/{g.user.username}/trips/{trip_id}")

@app.route("/trips/<trip_id>/delete", methods=["POST"])
def delete_trip(trip_id):
    """
    Handles deleting a trip.
    Redirects to user's planned trips.
    """
    remove = RemoveButton()

    if remove.validate_on_submit():
        Trip.delete(trip_id)

    return redirect(f"/users/{g.user.username}/trips")