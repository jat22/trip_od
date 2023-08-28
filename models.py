from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

from functions import get_all_activities, trip_dates, make_date_range, get_poi_details
from datetime import timedelta

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)
    
class User(db.Model):
	__tablename__ = "users"

	username = db.Column(db.Text, primary_key=True, autoincrement=False)
	email = db.Column(db.Text, unique=True)
	password = db.Column(db.Text, nullable=False)
	first_name = db.Column(db.Text)
	last_name = db.Column(db.Text)
	trips = db.relationship("Trip", cascade="all, delete")
	
	def __repr__(self):
		return f"<User:{self.username}>"
		
	@classmethod
	def signup(cls, username, email, first_name, last_name, password):
		hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

		user = User(
			username=username, 
	     	email=email,
			first_name=first_name,
			last_name=last_name,
			password=hashed_pwd
		)

		db.session.add(user)

	@classmethod
	def authenticate(cls, username, password):
		user = cls.query.filter_by(username=username).first()

		if user:
			if bcrypt.check_password_hash(user.password, password):
				return user
		
		return False
	
class Park(db.Model):
	__tablename__ = "parks"

	code = db.Column(db.Text, primary_key=True)
	api_id = db.Column(db.Text)
	name = db.Column(db.Text, nullable=False)
	url = db.Column(db.Text)
	lat = db.Column(db.Text)
	lon = db.Column(db.Text)
    
	def __repr__(self):
		return f"<Park:{self.name} Code:{self.code}>"

	@classmethod
	def create(cls, code, api_id, name, url, lat, lon):
		new = cls(
			code = code,
			api_id = api_id,
			name = name, 
			url = url,
			lat = lat,
			lon = lon
		)
	    
		db.session.add(new)
		db.session.commit()
	
class Trip(db.Model):
	__tablename__ = "trips"

	id = db.Column(db.Integer, primary_key=True)
	start_date = db.Column(db.Date)
	end_date = db.Column(db.Date)
	notes = db.Column(db.Text)
	username = db.Column(db.ForeignKey("users.username", ondelete="CASCADE"))
	park_code = db.Column(db.ForeignKey("parks.code", ondelete="SET NULL"))
	park = db.Relationship("Park", backref="trips")

	def __repr__(self):
		return f"<Trip #{self.id}: {self.park.name} for {self.username}>"
	
	@classmethod
	def create(cls, start_date, end_date, notes, username, park_code):
		trip = Trip(
	    	start_date = start_date, 
			end_date = end_date,
			notes = notes,
			username = username,
			park_code = park_code)
		db.session.add(trip)
		db.session.commit()

		trip_days = trip_dates(start_date, end_date)

		for d in trip_days:
			new_day = TripDay(
                trip_id = trip.id,
                date = d["datetime"],
                dow = d["dow"],
                year = d["year"],
                month = d["month"],
                day = d["day"]
            )
			db.session.add(new_day)
			db.session.commit()
		
		return trip
	
	@classmethod
	def update(cls, trip, notes, start_date, end_date):
		trip_days = trip.days
		if trip.start_date != start_date and trip.start_date > start_date:
			TripDay.create(start_date, (trip.start_date - timedelta(days=1)), trip.id)
		if trip.start_date != start_date and trip.start_date < start_date:
			TripDay.delete(trip.start_date, (start_date - timedelta(days=1)), trip_days)
		if trip.end_date != end_date and trip.end_date > end_date:
			TripDay.delete((end_date + timedelta(days=1)), trip.end_date, trip_days)
		if trip.end_date != end_date and trip.end_date < end_date:
			TripDay.create((trip.end_date + timedelta(days=1)), end_date, trip.id)

		trip.notes = notes
		trip.start_date = start_date
		trip.end_date = end_date

		db.session.commit()



class Campground(db.Model):
	__tablename__ = "campgrounds"

	id = db.Column(db.Text, primary_key=True)
	name = db.Column(db.Text, nullable=False)
	url = db.Column(db.Text)
	lat = db.Column(db.Text)
	lon = db.Column(db.Text)
	park_code = db.Column(db.ForeignKey("parks.code", ondelete="CASCADE"))
	park = db.Relationship("Park", backref="campgrounds")

	def __repr__(self):
		return f"<Campground:{self.name}>"
	
	@classmethod
	def create(cls, id, name, url, lat, lon, park_code):
		new = cls(
			id = id,
			name = name,
			url = url,
			lat = lat,
			lon = lon,
			park_code = park_code
		)

		db.session.add(new)
		db.session.commit()


class ThingToDo(db.Model):
	__tablename__ = "things_to_do"

	id = db.Column(db.Text, primary_key=True)
	park_code = db.Column(db.ForeignKey("parks.code", ondelete="CASCADE"))
	title = db.Column(db.Text, nullable=False)
	url = db.Column(db.Text)

	def __repr__(self):
		return f"<ThingToDo: {self.title}>"

	@classmethod
	def create(cls, id, park_code, title, url):
		new_thing = cls(
			id = id,
			park_code = park_code,
			title = title,
			url = url
		)
		db.session.add(new_thing)
		db.session.commit()

class TripDay(db.Model):
	__tablename__ = "trip_days"

	id = db.Column(db.Integer, primary_key=True)
	trip_id = db.Column(db.ForeignKey("trips.id", 
				   ondelete="CASCADE"), 
				   nullable=False)
	date = db.Column(db.Date, nullable=False)
	dow = db.Column(db.Text)
	year = db.Column(db.Text)
	month = db.Column(db.Text)
	day = db.Column(db.Text)
	campground_id = db.Column(db.ForeignKey("campgrounds.id"), nullable=True)
	campgrounds = db.Relationship("Campground")
	things_to_do = db.Relationship("ThingToDo", secondary="day_things_to_do")
	trip = db.Relationship("Trip", backref="days")

	def __repr__(self):
		return f"<TripDay Trip#{self.trip_id} date: {self.date}>"
	
	@classmethod
	def create(cls, start_date, end_date, trip_id):
		new_trip_days = trip_dates(start_date, end_date)
		for d in new_trip_days:
			new_day = TripDay(
				trip_id = trip_id,
				date = d["datetime"],
				dow = d["dow"],
				year = d["year"],
				month = d["month"],
				day = d["day"]
			)
			db.session.add(new_day)
			db.session.commit()
	
	@classmethod
	def delete(cls, start_date, end_date, trip_days):
		del_days = make_date_range(start_date, end_date)
		for day in trip_days:
			if day.date in del_days:
				db.session.delete(day)
				db.session.commit()

	@classmethod
	def remove_campground(cls, id):
		to_update = TripDay.query.get(id)
		to_update.campground_id = None

		db.session.commit()

class DayThingsToDo(db.Model):
	__tablename__ = "day_things_to_do"

	id = db.Column(db.Integer, primary_key=True)
	day_id = db.Column(db.ForeignKey("trip_days.id", ondelete="CASCADE"))
	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"))
	thing_id = db.Column(db.ForeignKey("things_to_do.id", ondelete="CASCADE"))
	thing = db.Relationship("ThingToDo")

	@classmethod
	def create(cls, day_id, trip_id, thing_id):
		new_day_thing = cls(
			day_id=day_id,
			trip_id=trip_id,
			thing_id=thing_id
		)
		db.session.add(new_day_thing)
		db.session.commit()
	
	@classmethod
	def remove(cls, id):
		to_remove = DayThingsToDo.query.get(id)

		db.session.delete(to_remove)
		db.session.commit()

class SavedThingToDo(db.Model):
	__tablename__ = "saved_things_to_do"

	id = db.Column(db.Integer, primary_key=True)
	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"))
	thing_id = db.Column(db.ForeignKey("things_to_do.id", ondelete="CASCADE"))
	trip = db.Relationship("Trip", backref="saved_things_to_do")
	thing = db.Relationship("ThingToDo")

	@classmethod
	def create(cls, trip_id, thing_id):
		new_saved = cls(
			trip_id = trip_id,
			thing_id = thing_id
		)

		db.session.add(new_saved)
		db.session.commit()
	
	@classmethod
	def remove(cls, id):
		to_remove = SavedThingToDo.query.get(id)

		db.session.delete(to_remove)
		db.session.commit()

class SavedCampground(db.Model):
	__tablename__ = "saved_campgrounds"

	id = db.Column(db.Integer, primary_key=True)
	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"))
	campground_id = db.Column(db.ForeignKey("campgrounds.id", ondelete="CASCADE"))
	trip = db.Relationship("Trip", backref="saved_campgrounds")
	campground = db.Relationship("Campground")

	@classmethod
	def create(cls, trip_id, campground_id):
		new_saved = cls(
			trip_id = trip_id,
			campground_id = campground_id
		)

		db.session.add(new_saved)
		db.session.commit()
	
	@classmethod
	def remove(cls, id):
		to_remove = SavedCampground.query.get(id)

		db.session.delete(to_remove)
		db.session.commit() 