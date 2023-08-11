from app import app
from models import db, Trip, User, POI, TripDay, TripDayPoiAct, DayPoi, Activity
import datetime

db.drop_all()
db.create_all()

Activity.update_activities()

user1 = User.signup(
    username = "user1",
    email = "user1@email.com",
	first_name = "User",
    last_name = "One",
    password = "password"
)

user2 = User.signup(
    username = "user2",
    email = "user2@email.com",
	first_name = "User",
    last_name = "Two",
    password = "password"
)

user3 = User.signup(
    username = "user3",
    email = "user3@email.com",
	first_name = "User",
    last_name = "Three",
    password = "password"
)

db.session.commit()

trip1 = Trip.create_trip(
    name = "Smoky Mountains",
    start_date = datetime.datetime(2023, 7, 1),
    end_date = datetime.datetime(2023, 7, 4),
    notes = "Walking through the mountains",
    username = "user1"
)

trip2 = Trip.create_trip(
    name = "Salt Lake City",
    start_date = datetime.datetime(2023, 8, 1),
    end_date = datetime.datetime(2023, 8, 4),
    notes = "We need salt!",
    username = "user1"
)

# trip2.lat = "40.7608"
# trip2.long = "-111.8910"


trip3 = Trip.create_trip(
    name = "West Coast Baby",
    start_date = datetime.datetime(2023, 6, 1),
    end_date = datetime.datetime(2023, 6, 4),
    notes = "Visiting Seaside",
    username = "user2"
)

# trip3.lat = "45.9932",
# trip3.long = "-123.9226",


trip4 = Trip.create_trip(
    name = "Vermont",
    start_date = datetime.datetime(2023, 8, 15),
    end_date = datetime.datetime(2023, 8, 20),
    notes = "The Long Trail!",
    username = "user3"
)

# trip4.lat = "43.6106"
# trip4.long = "-72.9726"

db.session.commit()

poi1 = POI.create_poi(
    id = "ts123", 
    name = "test-place", 
    type = "test-type", 
    subtype = "subtype", 
    lat = "11.11", 
    long = "22.22"
)

poi2 = POI.create_poi(
    id = "ts222", 
    name = "test-place2", 
    type = "test-type2", 
    subtype = "subtype2", 
    lat = "11.11", 
    long = "22.22"
)

poi1 = POI.create_poi(
    id = "ts333", 
    name = "test-place3", 
    type = "test-type3", 
    subtype = "subtype3", 
    lat = "11.11", 
    long = "22.22"
)
db.session.commit()

