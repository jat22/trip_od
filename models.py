from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

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
	notes = db.Column(db.Text)
	username = db.Column(db.ForeignKey("users.username", ondelete="CASCADE"))
	days = db.Relationship("TripDay", backref="trip", cascade="all, delete")
	pois = db.Relationship("POI", secondary="trip_day_poi_act")
	activities = db.Relationship("Activity",
			      secondary="trip_day_poi_act")
	possibilities = db.Relationship("Possibility", backref="trip")
	

	def __repr__(self):
		return f"<Trip #{self.id}: {self.name} for {self.username}>"
	
	@classmethod
	def create_trip(cls, name, start_date, end_date, notes, username):
		trip = Trip(
			name = name,
	    	start_date = start_date, 
			end_date = end_date,
			notes = notes,
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
	
	@classmethod
	def update(cls, trip, name, notes, start_date, end_date):
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
		trip.notes = notes
		trip.start_date = start_date
		trip.end_date = end_date
		db.session.commit()


class POI(db.Model):
	__tablename__ = "pois"

	id = db.Column(db.Text, primary_key=True, autoincrement=False)
	name = db.Column(db.Text)
	type = db.Column(db.Text)
	subtype = db.Column(db.Text)
	lat = db.Column(db.Text)
	long = db.Column(db.Text)
	day_acts = db.Relationship("TripDayPoiAct", backref="pois")

	def __repr__(self):
		return f"<POI #{self.id}: {self.name}>"

	@classmethod
	def create_poi(cls, id, name, type, subtype, lat, long):

		poi = POI(
			id = id,
			name = name,
			type = type,
			subtype = subtype,
			lat = lat,
			long = long
		)
		db.session.add(poi)
		db.session.commit()

class TripDay(db.Model):
	__tablename__ = "trip_days"

	id = db.Column(db.Integer, primary_key=True)
	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
	date = db.Column(db.Date, nullable=False)
	dow = db.Column(db.Text)
	year = db.Column(db.Text)
	month = db.Column(db.Text)
	day = db.Column(db.Text)
	stay_id = db.Column(db.ForeignKey("pois.id"), nullable=True)
	stay = db.Relationship("POI")
	pois = db.Relationship("POI", secondary="trip_day_poi_act")
	
	def __repr__(self):
		return f"<TripDay Trip#{self.trip_id} date: {self.date}>"

	def addStay(self, stay_id):
		self.stay_id = stay_id
		print(self.id)
		db.session.add(self)


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
	day_acts = db.Relationship("TripDayPoiAct", backref="activities")
	
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

class TripDayPoiAct(db.Model):
	__tablename__ = "trip_day_poi_act"
	
	id = db.Column(db.Integer, primary_key=True)
	trip_id = db.Column(db.ForeignKey("trips.id", 
				   ondelete="CASCADE"), 
				   nullable=False)
	day_id = db.Column(db.ForeignKey("trip_days.id", 
				  ondelete="CASCADE"), 
				  nullable=True)
	poi_id = db.Column(db.ForeignKey("pois.id"), nullable=False)
	act_id = db.Column(db.ForeignKey("activities.id"), nullable=True)
	trip = db.Relationship("Trip", backref="day_acts")
	day = db.Relationship("TripDay")
	poi = db.Relationship("POI")
	activity = db.Relationship("Activity")

	@classmethod
	def add(cls, trip_id, date, act_id, poi_id):
		print('METHOD##################################')
		print(poi_id)
		trip_day = TripDay.query.filter(
			TripDay.date == date, TripDay.trip_id == trip_id
			).first()
		
		new_tdpa = TripDayPoiAct(
			trip_id = trip_id,
			day_id = trip_day.id,
			poi_id = poi_id,
			act_id = act_id
		)

		db.session.add(new_tdpa)
		db.session.commit()

class Possibility(db.Model):
	__tablename__ = "possibilities"
 
	id = db.Column(db.Integer, primary_key=True)
	trip_id = db.Column(db.ForeignKey("trips.id", 
				   ondelete="CASCADE"), 
				   nullable=False)
	poi_id = db.Column(db.ForeignKey("pois.id"))
	act_id = db.Column(db.ForeignKey("activities.id"))
	type = db.Column(db.Text, nullable=False)
	name = db.Column(db.Text)
	
	




















	# activity_id = db.Column(db.ForeignKey("activities")),

	# trip_poi_activity_id = db.Column(db.ForeignKey("trip_poi_activity.id", ondelete="CASCADE"))




# class UTripCamp(db.Model):
# 	__tablename__ = "u_camps"

# 	id = db.Column(db.Integer, primary_key=True)
# 	location_id = db.Column(db.ForeignKey("locations.id"), nullable=False)
# 	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

# class UTripAct(db.Model):
# 	__tablename__ = "u_acts"

# 	id = db.Column(db.Integer, primary_key=True)
# 	act_id = db.Column(db.ForeignKey("activities.id"), nullable=False)
# 	location_id = db.Column(db.ForeignKey("locations.id"), nullable=False)
# 	trip_id = db.Column(db.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

# day_acts = db.Relationship("TripDayPoiAct")
	
	# pois = db.Relationship("POI", secondary="trip_poi_activity", backref="trips")
	# u_camps = db.Relationship("Location",
	# 			  secondary="u_camps", cascade="all, delete")
	# u_acts = db.Relationship("UTripAct", cascade="all, delete")

# day_acts = db.Relationship("DayActivity", backref="location", cascade="all, delete")
	# u_acts = db.Relationship("UTripAct", backref="location", cascade="all, delete")
	# trip_day = db.Relationship("TripDay", backref="location", cascade="all, delete")
	# u_camps = db.Relationship("UTripCamp", backref="location", cascade="all, delete")
	# trip_day = db.Relationship("TripDay", backref="camp", cascade="all, delete")


# class TripDayPoiAct(db.Model):
# 	__tablename__ = "trip_day_poi_act"

# 	id = db.Column(db.Integer, primary_key=True)
# 	trip_id = db.Column(db.ForeignKey("trips.id"), nullable=False)
# 	trip_day_id = db.Column(db.ForeignKey("trip_days.id", ondelete="CASCADE"), nullable=False)
# 	poi_id = db.Column(db.ForeignKey("pois.id"), nullable=False)
# 	act_id = db.Column(db.ForeignKey("activities.id"), nullable=False)
# 	activity = db.relationship("Activity")

# class PoiAct(db.Model):
# 	__tablename__ = "poi-acts"

# 	id = db.Column(db.Integer, primary_key=True)
# 	poi_id = db.Column(db.ForeignKey("pois.id"))
# 	activity_id = db.Column(db.ForeignKey("activities.id"))
# 	poi = db.Relationship("POI")
# 	act = db.Relationship("Activity")

# class DayPoi(db.Model):
# 	__tablename__ = "day_pois"

# 	id = db.Column(db.Integer, primary_key=True)
# 	trip_day_id = db.Column(db.ForeignKey("trip_days.id", ondelete="CASCADE"), nullable=False)
# 	notes = db.Column(db.Text)
# 	poi_id = db.Column(db.ForeignKey("pois.id"))
# 	trip_day_poi_act_id = db.Column(db.ForeignKey("trip_day_poi_act.id"))
# 	poi = db.relationship("POI")

# 	@classmethod
# 	def get_poi_activities(self, poi_id, trip_day_id):
# 		results = TripDayPoiAct.query.filter(
# 			and_(
# 				TripDayPoiAct.poi_id == poi_id, 
# 				TripDayPoiAct.trip_day_id == trip_day_id
# 				).all()
# 			)
# 		activities = []
# 		for result in results:
# 			activities.append(result.activity.name)
# 		return activities