from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from functions import get_all_activities, trip_dates, make_date_range
from datetime import timedelta

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)
    
class User(db.Model):
	__tablename__ = "users"

	username = db.Column(db.Text, primary_key=True, autoincrement=False)
	email = db.Column(db.Text)
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
	
class Trip(db.Model):
	__tablename__ = "trips"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.Text, nullable=False)
	start_date = db.Column(db.Date)
	end_date = db.Column(db.Date)
	lat = db.Column(db.Text)
	long = db.Column(db.Text)
	description = db.Column(db.Text)
	username = db.Column(db.ForeignKey("users.username", ondelete="CASCADE"))
	days = db.Relationship("TripDay", backref="trip", cascade="all, delete")
	u_camps = db.Relationship("Location",
				  secondary="u_camps", cascade="all, delete")
	u_acts = db.Relationship("UTripAct", cascade="all, delete")
	

	def __repr__(self):
		return f"<Trip #{self.id}: {self.name} for {self.username}>"
	
	@classmethod
	def create_trip(cls, name, start_date, end_date, description, username):
		trip = Trip(
			name = name,
	    	start_date = start_date, 
			end_date = end_date,
			description = description,
			username = username)
		db.session.add(trip)
		db.session.commit()

		cls.create_trip_days(trip.id, start_date, end_date)
		
		return trip
	
	@classmethod
	def create_trip_days(cls, trip_id, start_date, end_date):
		trip_days = trip_dates(start_date, end_date)

		for d in trip_days:
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
	def update(cls, trip, name, description, start_date, end_date):
		trip_days = trip.days
		if trip.start_date != start_date and trip.start_date > start_date:
			TripDay.add(start_date, (trip.start_date - timedelta(days=1)), trip.id)
		if trip.start_date != start_date and trip.start_date < start_date:
			TripDay.delete(trip.start_date, (start_date - timedelta(days=1)), trip_days)
		if trip.end_date != end_date and trip.end_date > end_date:
			TripDay.delete((end_date + timedelta(days=1)), trip.end_date, trip_days)
		if trip.end_date != end_date and trip.end_date < end_date:
			TripDay.add((trip.end_date + timedelta(days=1)), end_date, trip.id)
		trip.name = name
		trip.description = description
		trip.start_date = start_date
		trip.end_date = end_date
		db.session.commit()


class Location(db.Model):
	__tablename__ = "locations"

	id = db.Column(db.Text, primary_key=True, autoincrement=False)
	name = db.Column(db.Text)
	phone = db.Column(db.Text)
	email = db.Column(db.Text)
	description = db.Column(db.Text)
	directions = db.Column(db.Text)
	address = db.Column(db.Text)
	city = db.Column(db.Text)
	state = db.Column(db.Text)
	zip = db.Column(db.Text)
	lat = db.Column(db.Text)
	long = db.Column(db.Text)
	links = db.Relationship("Link")
	day_acts = db.Relationship("DayActivity", backref="location", cascade="all, delete")
	u_acts = db.Relationship("UTripAct", backref="location", cascade="all, delete")
	trip_day = db.Relationship("TripDay", backref="location", cascade="all, delete")
	u_camps = db.Relationship("UTripCamp", backref="location", cascade="all, delete")
	trip_day = db.Relationship("TripDay", backref="camp", cascade="all, delete")

	def __repr__(self):
		return f"<Location #{self.id}: {self.name}>"

	@classmethod
	def create_location(cls, id, name, phone, email, description, directions, address, city, state, zip, lat, long, links):

		location = Location(
			id = id,
			name = name,
			phone = phone,
			email = email,
			description = description,
			directions = directions,
			address = address,
			city = city,
			state = state,
			zip = zip,
			lat = lat,
			long = long
		)
		db.session.add(location)
		db.session.commit()

		for link in links:
			new_link = Link(**link)
			db.session.add(new_link)
			db.session.commit()


class Link(db.Model):
	__tablebane__ = "links"

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.Text)
	url = db.Column(db.Text)
	location_id = db.Column(db.ForeignKey("locations.id", ondelete="CASCADE"))

class TripDay(db.Model):
	__tablename__ = "trip_days"

	id = db.Column(db.Integer, primary_key=True)
	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
	date = db.Column(db.Date, nullable=False)
	dow = db.Column(db.Text)
	year = db.Column(db.Text)
	month = db.Column(db.Text)
	day = db.Column(db.Text)
	camp_id = db.Column(db.ForeignKey("locations.id"), nullable=True)
	day_acts = db.Relationship("DayActivity", backref="trip_day", cascade="all, delete")
	
	def __repr__(self):
		return f"<TripDay Trip#{self.trip_id} date: {self.date}>"

	@classmethod
	def add(cls, start_date, end_date, trip_id):
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

class Activity(db.Model):
	__tablename__ = "activities"
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.Text)
	day_act = db.Relationship("DayActivity", backref="activity")
	u_acts = db.Relationship("UTripAct", backref="activity")
	
	def __repr__(self):
		return f"<Activity: {self.name}>"
	
	@classmethod
	def update_activities(self):
		activities = get_all_activities()
		existing_act_ids = [id[0] for id in db.session.query(Activity.id).all()]

		for activity in activities:
			if activity["id"] not in existing_act_ids:
				new_activity = Activity(
					id=activity["id"],
					name=activity["name"]
				)
				db.session.add(new_activity)
				db.session.commit()


class DayActivity(db.Model):
	__tablename__ = "day_acts"

	id = db.Column(db.Integer, primary_key=True)
	trip_day_id = db.Column(db.ForeignKey("trip_days.id", ondelete="CASCADE"), nullable=False)
	act_id = db.Column(db.ForeignKey("activities.id"))
	location_id = db.Column(db.ForeignKey("locations.id"), nullable=False)

class UTripCamp(db.Model):
	__tablename__ = "u_camps"

	id = db.Column(db.Integer, primary_key=True)
	location_id = db.Column(db.ForeignKey("locations.id"), nullable=False)
	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

class UTripAct(db.Model):
	__tablename__ = "u_acts"

	id = db.Column(db.Integer, primary_key=True)
	act_id = db.Column(db.ForeignKey("activities.id"), nullable=False)
	location_id = db.Column(db.ForeignKey("locations.id"), nullable=False)
	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

