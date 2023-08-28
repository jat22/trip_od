from appOG import app
from models import db, Trip, User, Park, Campground, ThingToDo, DayThingsToDo, SavedCampground, SavedThingToDo
import datetime

db.drop_all()
db.create_all()

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

test_park1 = Park.create(
    code = "abcd",
    api_id = "!@#$%12354",
    name = "Test Park 1",
    url = "www.testpark1.com",
    lat = "123.34",
    lon = "123.34"
)

test_park2 = Park.create(
    code = "efgh",
    api_id = "!@#$%22354",
    name = "Test Park 2",
    url = "www.testpark2.com",
    lat = "223.34",
    lon = "223.34"
)

test_park3 = Park.create(
    code = "ijkl",
    api_id = "!@#$%32354",
    name = "Test Park 3",
    url = "www.testpark3.com",
    lat = "323.34",
    lon = "323.34"
)

trip1 = Trip.create(
    start_date = datetime.datetime(2023, 7, 1),
    end_date = datetime.datetime(2023, 7, 4),
    notes = "Walking through the mountains",
    username = "user1",
    park_code = "abcd"
)

trip2 = Trip.create(
    start_date = datetime.datetime(2023, 8, 1),
    end_date = datetime.datetime(2023, 8, 4),
    notes = "We need salt!",
    username = "user1",
    park_code = "efgh"
)

trip3 = Trip.create(
    start_date = datetime.datetime(2023, 6, 1),
    end_date = datetime.datetime(2023, 6, 4),
    notes = "Visiting Seaside",
    username = "user2",
    park_code = "ijkl"
)

trip4 = Trip.create(
    start_date = datetime.datetime(2023, 8, 15),
    end_date = datetime.datetime(2023, 8, 20),
    notes = "The Long Trail!",
    username = "user3",
    park_code = "ijkl"
)

campground1 = Campground.create(
    id = "campground1",
    name = "Campground One",
    url = "qqq.aasd",
    lat = "123",
    lon = "234",
    park_code = "abcd"
)

campground2 = Campground.create(
    id = "campground2",
    name = "Campground Two",
    url = "qqq.aasd",
    lat = "123",
    lon = "234",
    park_code = "ijkl"
)

campground3 = Campground.create(
    id = "campground3",
    name = "Campground Three",
    url = "qqq.aasd",
    lat = "123",
    lon = "234",
    park_code = "efgh"
)

thing_to_do_1 = ThingToDo.create(
    id = "thing1",
    park_code = "abcd",
    title = "Thing One",
    url = "url1"
)

thing_to_do_2 = ThingToDo.create(
    id = "thing2",
    park_code = "efgh",
    title = "Thing Two",
    url = "url2"
)

thing_to_do_1 = ThingToDo.create(
    id = "thing3",
    park_code = "ijkl",
    title = "Thing Three",
    url = "url3"
)