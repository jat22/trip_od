from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from datetime import timedelta

from find import Find
from helpers import Helpers

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
	name = db.Column(db.Text, nullable=False)
	url = db.Column(db.Text)
	lat = db.Column(db.Text)
	lon = db.Column(db.Text)

    
	def __repr__(self):
		return f"<Park:{self.name} Code:{self.code}>"

	@classmethod
	def create(cls, code):
		park_details = Find.park_details(code)

		new = cls(
			code = code,
			name = park_details.get("name"), 
			url = park_details.get("url"),
			lat = park_details.get("lat"),
			lon = park_details.get("lon")
		)

		db.session.add(new)
		db.session.commit()
	    
		for thing in park_details.get("things_to_do"):
			ThingToDo.create(
				id = thing.get("id"),
				park_code = code,
				title = thing.get("title"),
				url = thing.get("url")
			)

		for campground in park_details.get("campgrounds"):
			Campground.create(
				id = campground.get("id"),
				name = campground.get("name"),
				url = campground.get("url"),
				lat = campground.get("lat"),
				lon = campground.get("lon"),
				park_code = code
			)
	
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
	def create(cls, start_date, end_date, username, park_code):
		check_park = Park.query.get(park_code)
		
		if(not check_park):
			Park.create(park_code)

		trip = cls(
	    	start_date = start_date, 
			end_date = end_date,
			username = username,
			park_code = park_code)
		db.session.add(trip)
		db.session.commit()

		trip_days = Helpers.generate_trip_dates(start_date, end_date)

		for d in trip_days:
			new_day = TripDay(
                trip_id = trip.trip_id,
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
	def delete(cls, trip_id):
		trip = Trip.query.get(trip_id)

		for day in trip.days:
			day.delete_day()

		db.session.delete(trip)
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
	park = db.Relationship("Park", backref="things_to_do")

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
				   ondelete='CASCADE'), 
				   nullable=False)
	date = db.Column(db.Date, nullable=False)
	dow = db.Column(db.Text)
	year = db.Column(db.Text)
	month = db.Column(db.Text)
	day = db.Column(db.Text)
	campground_id = db.Column(db.ForeignKey("campgrounds.id"), nullable=True)
	campground = db.Relationship("Campground")
	things_to_do = db.Relationship("ThingToDo", secondary="day_things_to_do")
	trip = db.Relationship("Trip", backref="days")

	def __repr__(self):
		return f"<TripDay Trip#{self.trip_id} date: {self.date}>"
	
	@classmethod
	def create(cls, start_date, end_date, trip_id):
		new_trip_days = Helpers.trip_dates(start_date, end_date)
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
		del_days = Helpers.make_date_range(start_date, end_date)
		for day in trip_days:
			if day.date in del_days:
				db.session.delete(day)
				db.session.commit()
	
	@classmethod
	def add_campground(cls, day_id, campground_id):
		day = TripDay.query.get(day_id)
		day.campground_id = campground_id

		db.session.commit()
		

	@classmethod
	def remove_campground(cls, day_id):
		to_update = TripDay.query.get(day_id)
		to_update.campground_id = None

		db.session.commit()

	def delete_day(self):
		db.session.delete(self)
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
	def remove(cls, day_id, thing_id):
		to_remove = DayThingsToDo.query.filter(and_(DayThingsToDo.day_id==day_id, thing_id==DayThingsToDo.thing_id)).first()

		db.session.delete(to_remove)
		db.session.commit()