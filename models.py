from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)
    
class User(db.Model):
	__tablename__ = "users"

	username = db.Column(db.Text, primary_key=True, autoincrement=False)
	email = db.Column(db.Text, nullable=False)
	password = db.Column(db.Text, nullable=False)
	first_name = db.Column(db.Text)
	last_name = db.Column(db.Text)
	
	def __repr__(self):
		return f"<User:{self.username}>"
		
	@classmethod
	def signup(cls, username, email, password):
		hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

		user = User(username=username, email=email, password=hashed_pwd)

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
	description = db.Column(db.Text)
	user = db.Column(db.ForeignKey("users.username"))

	def __repr__(self):
		return f"<Trip #{self.id}: {self.name} for {self.user}>"

class Location(db.Model):
	__tablename__ = "locations"

	id = db.Column(db.Text, primary_key=True, autoincrement=False)
	name = db.Column(db.Text)
	lat = db.Column(db.Float)
	long = db.Column(db.Float)

	def __repr__(self):
		return f"<Location #{self.id}: {self.name}>"

class Activity(db.Model):
	__tablename__ = "activities"

	name = db.Column(db.Text, primary_key=True, nullable=False)
	
	def __repr__(self):
		return f"<Activity: {self.name}>"
	
	# @classmethod
	# def update_activities(self):
	# 	activities = get_all_activities()
	# 	existing_act_ids = [id[0] for id in db.session.query(Activity.id).all()]

	# 	for activity in activities:
	# 		if activity["id"] not in existing_act_ids:
	# 			new_activity = Activity(
	# 				id=activity["id"],
	# 				name=activity["name"]
	# 			)
	# 		db.session.add(new_activity)
	# 	db.session.commit()

class TripDay(db.Model):
	__tablename__ = "trip_days"

	id = db.Column(db.Integer, primary_key=True)
	trip_id = db.Column(db.ForeignKey("trips.id"), nullable=False)
	date = db.Column(db.Date, nullable=False)
	campground = db.Column(db.ForeignKey("campgrounds.id"))
	
	def __repr__(self):
		return f"<TripDay Trip#{self.trip_id} date: {self.date}>"

class DayActivity(db.Model):
	__tablename__ = "day_acts"

	id = db.Column(db.Integer, primary_key=True)
	trip_day = db.Column(db.ForeignKey("trip_days.id"), nullable=False)
	activity = db.Column(db.ForeignKey("activities.name"))
	location = db.Column(db.ForeignKey("locations.id"))

class Campground(db.Model):
	__tablename__ = "campgrounds"

	id = db.Column(db.Text, primary_key=True, autoincrement=False)
	name = db.Column(db.Text, nullable=False)
	lat = db.Column(db.Float)
	long = db.Column(db.Float)

	def __repr__(self):
		return f"<Campground #{self.id}: {self.name}>"
	
class UnassignedTripCampground(db.Model):
	__tablename__ = "usgnd_campgrounds"

	id = db.Column(db.Integer, primary_key=True)
	campground = db.Column(db.ForeignKey("campgrounds.id"))
	trip = db.Column(db.ForeignKey("trips.id"))

class UnassignedTripActivities(db.Model):
	__tablename__ = "usgnd_acts"

	id = db.Column(db.Integer, primary_key=True)
	campground = db.Column(db.ForeignKey("activities.name"))
	trip = db.Column(db.ForeignKey("trips.id"))