from flask import Flask, redirect, render_template, url_for, request, flash, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
import config, random, json

from data import states
from models import connect_db, db, User, Trip, POI, TripDay, DayActivity, TripPoiActivity, bcrypt, Activity
from forms import CreateAccountForm, CreateTripForm, LoginForm, EditUserForm, DescriptionUpdateForm, TripUpdateForm
from functions import search_by_location, get_poi_details, display_date, get_location_options, search_by_poi, search_by_location
from background_url import loc_bg_imgs, act_bg_imgs

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///rec_trips"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "secrets"

debug = DebugToolbarExtension(app)

connect_db(app)

# db.create_all()

# Activity.update_activities()

CURR_USER = "curr_user"
CURR_TRIP = "curr_trip"
REC_BASE_URL = "https://ridb.recreation.gov/api/v1"
GEOCODE_BASE_URL = "https://api.tomtom.com/search/2/geocode/"



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



@app.route("/")
def show_home():
    """show home page"""

    # if g.user:
    #     return redirect(f"/trips")

    # form = LoginForm()

    return render_template("landing.html", user=g.user, states=states)


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
            return render_template("/users/user-new.html", form=form)
        
        do_login(User.query.get(username))
        return redirect(f"/trips")
    
    else:
        return render_template("/users/user-new.html", form = form)

@app.route("/users/<username>")
def user_profile(username):
    """show current user's profile"""

    if not g.user:
            flash("Please Login or Create an Account")
            return redirect("/login")
    user = User.query.get(username)
    return render_template("users/user-profile.html", user=user)

@app.route("/users/<username>/edit", methods=["GET", "POST"])
def edit_user(username):
    """edit current user's profile"""

    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/login")
    edit_form = EditUserForm(obj=g.user)

    if edit_form.validate_on_submit():
        if User.authenticate(g.user.username, edit_form.password.data):
            g.user.email = edit_form.email.data
            g.user.first_name = edit_form.first_name.data
            g.user.last_name = edit_form.last_name.data
        else:
            flash("Incorrect Password", "danger")
            return redirect(f"/users/{g.user.username}")
        if edit_form.new_password.data:
            if edit_form.new_password.data == edit_form.pw_confirm.data:
                g.user.password = bcrypt.generate_password_hash(edit_form.new_password.data).decode('UTF-8')
            else:
                flash("New Password does not match", "danger")
                return redirect(f"/users/{g.user.username}/edit")
        db.session.commit()
        return redirect(f"/users/{g.user.username}")
    return render_template("/users/edit-user.html", form=edit_form, user=g.user)



####################### TRIP VIEW FUNCTIONS ##############################

@app.route("/trips/<int:trip_id>")
def show_a_trip(trip_id):
    """ display details of a particular trip """
    if not g.user:
            flash("Please Login or Create an Account")
            return redirect("/login")
    session[CURR_TRIP] = trip_id
    trip = Trip.query.get(trip_id)
    desc_form = DescriptionUpdateForm(obj=trip)
    trip_days = db.session.query(TripDay).filter(TripDay.trip_id==trip_id).order_by(TripDay.date).all()

    return render_template("/trip/trip-details.html", trip = trip, days=trip_days, form=desc_form)


@app.route("/trips/create", methods=["GET", "POST"])
def create_trip():
    """ get basic information about a new trip and
    create new trip that is attached to current, logged in user"""

    if not g.user:
            flash("Please Login or Create an Account")
            return redirect("/login")

    form = CreateTripForm()
    
    if form.validate_on_submit():
        if not g.user:
            flash("Please Login or Create an Account")
            return redirect("/login")
        
        start_date = form.start_date.data
        end_date = form.end_date.data
        if end_date >= start_date:
            new_trip = Trip.create_trip(
                    name = form.name.data,
                    start_date = start_date,
                    end_date = end_date,
                    description = form.description.data,
                    username = g.user.username
             )
        else:
             flash("Last day must be after First day.")
             return redirect('/trips/create')

        session[CURR_TRIP] = new_trip.id
        
        return redirect(f"/trips/{new_trip.id}")
    
    return render_template("/trip/create-trip.html", form=form)


@app.route("/trips/<int:trip_id>/where", methods=["GET"])
def trip_location(trip_id):
    """ get user input for location where they would like to visit """

    if not g.user:
            flash("Please Login or Create an Account")
            return redirect("/login")
    
    return render_template("/trip/search.html", trip_id=trip_id)
    

@app.route("/trips/<int:trip_id>/campgrounds")
def show_campgrounds(trip_id):
    """ show results for campgrounds based on location provided by user"""

    if not g.user:
            flash("Please Login or Create an Account")
            return redirect("/login")
    return render_template("/results/campgrounds.html", trip_id=trip_id)


# @app.route("/trips/<int:trip_id>/campgrounds/<location_id>/add", methods=["POST"])
# def add_campground(trip_id, location_id):
#     """add a campground to the current trip"""

#     if not g.user:
#             flash("Please Login or Create an Account")
#             return redirect("/login")
    
#     if not Location.query.get(location_id):
#         camp_data = get_location_details(location_id)
#         Location.create_location(**camp_data)

#     new_ucamp = UTripCamp(
#         location_id = location_id,
#         trip_id = trip_id
#     )
#     db.session.add(new_ucamp)
#     db.session.commit()
#     flash(f"{new_ucamp.location.name} added to your trip", "success")

#     return redirect(f"/trips/{trip_id}/campgrounds")


@app.route("/trips/<int:trip_id>/activities")
def show_activitiy_options(trip_id):
    """ display activity template; data is rendered by JS"""

    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/login")

    return render_template("/results/activities.html", trip_id=trip_id, base_url='BASE_URL', bg_img1=act_bg_imgs[random.randint(0,9)], bg_img2=act_bg_imgs[random.randint(0,9)], bg_img3=act_bg_imgs[random.randint(0,9)])

@app.route("/trips/<int:trip_id>/activity/<int:activity_id>")
def activity_locations(trip_id, activity_id):
    """ dispaly template for activities available at a particular location,
    data rendered by JS"""

    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/login")
    activity_name = Activity.query.get(activity_id).name

    return render_template("trip/activity-locations.html", trip_id=trip_id, activity_name=activity_name, activity_id=activity_id, bg_img1=act_bg_imgs[random.randint(0,9)], bg_img2=act_bg_imgs[random.randint(0,9)], bg_img3=act_bg_imgs[random.randint(0,9)])


# @app.route("/trips/<int:trip_id>/act<int:activity_id>/<location_id>/add", methods=["POST"])
# def add_activity_to_trip(trip_id, activity_id, location_id):
#     """adds a particular activity, attached to a particular location to the current trip"""

#     if not g.user:
#         flash("Please Login or Create an Account")
#         return redirect("/login")

#     if not Location.query.get(location_id):
#         location_data = get_location_details(location_id)
#         Location.create_location(**location_data)

#     new_uact = UTripAct(
#         act_id = activity_id,
#         location_id = location_id,
#         trip_id = trip_id
#     )
#     db.session.add(new_uact)
#     db.session.commit()

#     flash(f"Activity added to your trip", "success")

#     return redirect(f"/trips/{trip_id}/activities")



@app.route("/trips/<int:trip_id>/campground/assign", methods=["POST"])
def assign_campground(trip_id):
    """ assign a particular campground to a particular day """

    if not g.user:
            flash("Please Login or Create an Account")
            return redirect("/login")

    day_id = request.form.get("camp-day")
    if day_id:
        camp_id = request.form.get("location-id")


        trip_day = TripDay.query.get(day_id)
        if trip_day.camp_id:
            flash("A campground is already assigned, if you would like to replace it, please delete current campground.", "danger")

        trip_day.camp_id = camp_id
        db.session.add(trip_day)

        u_camp = UTripCamp.query.filter(and_(UTripCamp.location_id==camp_id, UTripCamp.trip_id==trip_id)).first()
        
        db.session.delete(u_camp)
        db.session.commit()
    else:
         flash("Please select a day.", "danger")

    return redirect(f"/trips/{trip_id}")

@app.route("/trips/<int:trip_id>/campground/delete", methods=["POST"])
def delete_campground(trip_id):
    """ remove a campground from a trip entirely """

    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/login")
    ucamp_id = request.form.get("ucampground-id")

    ucamp = UTripCamp.query.filter(and_(UTripCamp.location_id==ucamp_id, UTripCamp.trip_id==trip_id)).first()

    db.session.delete(ucamp)
    db.session.commit()

    return redirect(f"/trips/{trip_id}")

@app.route("/trips/<int:trip_id>/campground/unassign", methods=["POST"])
def unassign_campground(trip_id):
    """ unassign a campground from a particular day, but leave attached to the trip """

    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/login")

    trip_day = TripDay.query.get(request.form.get("day-id"))
    trip_day.camp_id = None

    ucamp = UTripCamp(
        location_id = request.form.get("campground-id"),
        trip_id = trip_day.trip_id
    )
    db.session.add(ucamp)
    db.session.commit()
    return redirect(f"/trips/{trip_id}")

@app.route("/trips/<int:trip_id>/activity/assign", methods=["POST"])
def assign_activity(trip_id):
    """ assign an activity(with a location) to a particular day """

    if not g.user:
            flash("Please Login or Create an Account")
            return redirect("/login")
    
    if request.form.get("act-day"):
        u_act = UTripAct.query.get(request.form.get("uact-id"))
        
        new_day_activity = DayActivity(
            trip_day_id = request.form.get("act-day"),
            act_id = u_act.act_id,
            location_id = u_act.location_id
        )

        db.session.add(new_day_activity)


        db.session.delete(u_act)
        db.session.commit()
    else:
        flash("Please select a date.", "danger")

    return redirect(f"/trips/{trip_id}")

@app.route("/trips/<int:trip_id>/activity/unassign", methods=["POST"])
def unassign_activity(trip_id):
    """ unassign an activity from a particular day """
    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/login")
    
    day_act = DayActivity.query.get(request.form.get("day-act-id"))

    uact = UTripAct(
         act_id = day_act.act_id,
         location_id = day_act.location.id,
         trip_id = trip_id
    )

    db.session.delete(day_act)
    db.session.add(uact)
    db.session.commit()
    return redirect(f"/trips/{trip_id}")

@app.route("/trips/<int:trip_id>/activity/delete", methods=["POST"])
def delete_activity(trip_id):
    """ remove an acitivty from a trip entirely"""

    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/login")

    uact = UTripAct.query.get(request.form.get("uact-id"))

    db.session.delete(uact)
    db.session.commit()

    return redirect(f"/trips/{trip_id}")

@app.route("/trips")
def show_mytrips():
    """ display a list of all of the current user's trips """

    if not g.user:
            flash("Please Login or Create an Account")
            return redirect("/login")

    trips = User.query.get(session[CURR_USER]).trips

    return render_template("trip/mytrips.html", trips=trips, display_date=display_date)

@app.route("/trips/<int:trip_id>/update", methods=["GET", "POST"])
def update_trip_info(trip_id):
    if not g.user:
        flash("Please Login or Create an Account")
        return redirect("/login")
    
    trip = Trip.query.get(trip_id)

    # desc_form = DescriptionUpdateForm(obj=trip)
    trip_form = TripUpdateForm(obj=trip)

    # if desc_form.validate_on_submit():
    #     trip.description = desc_form.description.data
    #     db.session.commit()
    #     return redirect(f"/trips/{trip_id}")

    if trip_form.validate_on_submit():
        Trip.update(
            trip = trip,
            name = trip_form.name.data,
            description = trip_form.description.data,
            start_date = trip_form.start_date.data,
            end_date = trip_form.end_date.data,
        )
        return redirect(f"/trips/{trip_id}")
    
    return render_template("/trip/update.html", form=trip_form, trip_id=trip.id)

@app.route("/trips/<int:trip_id>/confirm-delete")
def confirm_trip_delete(trip_id):
    trip = Trip.query.get(trip_id)
    form = TripUpdateForm(obj=trip)
    return render_template("/trip/confirm-delete.html", trip=trip, form=form)

@app.route("/trips/<int:trip_id>/delete")
def delete_trip(trip_id):
    trip = Trip.query.get(trip_id)

    db.session.delete(trip)
    db.session.commit()

    return redirect("/trips")


############################# LOCATION VIEW FUNCTIONS #########################

@app.route("/poi/<id>")
def show_poi_details(id):
    poi_details = get_poi_details(id)

    return render_template("results/poi-details.html", details = poi_details)



# @app.route("/locations/<location_id>")
# def show_location_details(location_id):
#     """ display details of a particular location """

#     if not g.user:
#             flash("Please Login or Create an Account")
#             return redirect("/login")
    
#     location_details = get_location_details(location_id)

#     return render_template("/trip/location-details.html", location=location_details, session=session, bg_img1=loc_bg_imgs[random.randint(0,9)], bg_img2=loc_bg_imgs[random.randint(0,9)])


# @app.route("/locations/<location_id>/activity/<int:activity_id>")
# def show_activity_location_details(location_id, activity_id):
#     """ display location details that is attached to a particular activity """

#     if not g.user:
#             flash("Please Login or Create an Account")
#             return redirect("/login")
    
#     location_details = get_location_details(location_id)
#     activity = Activity.query.get(activity_id)

#     return render_template("/trip/location-details.html", location=location_details, session=session, activity=activity, option=f"act{activity_id}", bg_img1=loc_bg_imgs[random.randint(0,9)], bg_img2=loc_bg_imgs[random.randint(0,9)])


# @app.route("/locations/<location_id>/campground")
# def show_campground_location_details(location_id):
#     """ display location details associcated with a particular campground """

#     if not g.user:
#             flash("Please Login or Create an Account")
#             return redirect("/login")
    
#     location_details = get_location_details(location_id)

#     return render_template("/trip/location-details.html", location=location_details, session=session, option="campgrounds", bg_img1=loc_bg_imgs[random.randint(0,9)], bg_img2=loc_bg_imgs[random.randint(0,9)])


################### SEACH APIs ##########################

@app.route("/search")
def search():
    data = json.loads(request.args.get('data'))
    
    if data.get("poi"):
        results = search_by_poi(data["term"], data["poi"])
    else:
        results = search_by_location(data["term"], data["lat"], data["lon"])

    fac_types = []
    for r in results:
        if r["type"] not in fac_types:
            fac_types.append(r["type"])  
    results_json = json.dumps(results)

    return render_template("searchResults.html", results=results, results_json=results_json, fac_types=fac_types)


@app.route("/api/geolocation")
def get_location():
    city = request.args.get("city")
    state = request.args.get("state")
    location_options = get_location_options(city, state)

    return jsonify(location_options)

@app.route("/api/search")
def search_():
    """ main search function using location input from user """

    results = search_by_location(
        city = request.args.get("city"),
        state = request.args.get("state"),
        latitude = request.args.get("latitude"),
        longitude = request.args.get("longitude"),
        radius = request.args.get("radius")
        )

    trip = Trip.query.get(request.args.get("tripId"))
    trip.lat = results['search_geolocation']['lat']
    trip.long = results['search_geolocation']['long']
    trip.radius = results['search_geolocation']['radius']
    db.session.commit()

    return jsonify(results)

@app.route("/api/trip/options")
def get_trip_options():

    """ gets campground and activitiy options for a trip based on location inform attached to the trip
        used to update information avaliable when the current trip is changed
    """

    trip = Trip.query.get(request.args.get("trip_id"))
    lat = trip.lat
    long = trip.long
    radius = ""

    results = search_by_location("", "", lat, long, radius)

    return jsonify(results)