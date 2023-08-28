from flask import Flask, redirect, render_template, request, flash, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from data import states
from models import connect_db, db, Trip, User, Park, Campground, ThingToDo, DayThingsToDo, SavedCampground, SavedThingToDo
from forms import CreateAccountForm, CreateTripForm, LoginForm, EditUserForm, DescriptionUpdateForm, TripUpdateForm
from keys import NPS_KEY

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///rec_trips"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SECRET_KEY'] = "secrets"

debug = DebugToolbarExtension(app)

connect_db(app)

CURR_USER = "curr_user"

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

################## LANDING PAGE ##########################
@app.route("/")
def show_home():
    """show home page"""

    state_names = list(states.keys())

    return render_template("landing.html", user=g.user, states=state_names)

################### USER VIEW FUNCTIONS #############################

@app.route('/login', methods=["GET", "POST"])
def login():
    """Show login page and login user"""

    form = LoginForm()

    if form.validate_on_submit():
        print("form validated")
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            return redirect('/')
        flash("Password/User incorrect", "danger")
    return render_template('/forms/login.html', form=form)

@app.route('/logout')
def logout():
    """Logout current user"""

    do_logout()
    flash("You are now logged out.", "success")
    return redirect('/')

@app.route("/signup", methods=["GET", "POST"])
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
            return render_template("/users/user-new.html", form=form)
        
        do_login(User.query.get(username))
        return redirect(f"/users/{username}/trips")
    
    else:
        return render_template("/forms/createAccount.html", form = form)