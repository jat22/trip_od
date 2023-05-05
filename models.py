from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from functions import get_all_activities, trip_dates

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
	trips = db.relationship("Trip")
	
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
	days = db.Relationship("TripDay", backref="trip")
	u_camps = db.Relationship("Location",
				  secondary="u_camps")
	u_acts = db.Relationship("UTripAct")
	

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
	day_acts = db.Relationship("DayActivity", backref="location")
	u_acts = db.Relationship("UTripAct", backref="location")
	trip_day = db.Relationship("TripDay", backref="location")
	u_camps = db.Relationship("UTripCamp", backref="location")
	trip_day = db.Relationship("TripDay", backref="camp")

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

	def __repr__(self):
		return f"<TripDay Trip#{self.trip_id} date: {self.date}>"

class Activity(db.Model):
	__tablename__ = "activities"
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.Text)
	day_act = db.Relationship("DayActivity", backref="activities")
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
	location_id = db.Column(db.ForeignKey("locations.id"))
	trip_day = db.Relationship("TripDay", backref="activity")


class UTripCamp(db.Model):
	__tablename__ = "u_camps"

	id = db.Column(db.Integer, primary_key=True)
	location_id = db.Column(db.ForeignKey("locations.id"))
	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"))

class UTripAct(db.Model):
	__tablename__ = "u_acts"

	id = db.Column(db.Integer, primary_key=True)
	act_id = db.Column(db.ForeignKey("activities.id"))
	location_id = db.Column(db.ForeignKey("locations.id"))
	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"))

