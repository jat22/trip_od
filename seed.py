from app import app
from models import db, Trip, User, Location, Link, TripDay, DayActivity, UTripCamp, UTripAct, Activity
import datetime

db.drop_all()
db.create_all()

Activity.update_activities()

user1 = User.signup(
    username = "user1",
    email = "user1@email.com",
	first_name = "User",
    last_name = "One",
    password = "user12345"
)

user2 = User.signup(
    username = "user2",
    email = "user2@email.com",
	first_name = "User",
    last_name = "Two",
    password = "user22345"
)

user3 = User.signup(
    username = "user3",
    email = "user3@email.com",
	first_name = "User",
    last_name = "Three",
    password = "user32345"
)

db.session.commit()

trip1 = Trip.create_trip(
    name = "Smoky Mountains",
    start_date = datetime.datetime(2023, 7, 1),
    end_date = datetime.datetime(2023, 7, 4),
    description = "Walking through the mountains",
    username = "user1"
)

trip1.lat= "35.6532"
trip1.long = "-83.5070"

trip2 = Trip.create_trip(
    name = "Salt Lake City",
    start_date = datetime.datetime(2023, 8, 1),
    end_date = datetime.datetime(2023, 8, 4),
    description = "We need salt!",
    username = "user1"
)

trip2.lat = "40.7608"
trip2.long = "-111.8910"


trip3 = Trip.create_trip(
    name = "West Coast Baby",
    start_date = datetime.datetime(2023, 6, 1),
    end_date = datetime.datetime(2023, 6, 4),
    description = "Visiting Seaside",
    username = "user2"
)

trip3.lat = "45.9932",
trip3.long = "-123.9226",


trip4 = Trip.create_trip(
    name = "Vermont",
    start_date = datetime.datetime(2023, 8, 15),
    end_date = datetime.datetime(2023, 8, 20),
    description = "The Long Trail!",
    username = "user3"
)

trip4.lat = "43.6106"
trip4.long = "-72.9726"

db.session.commit()

