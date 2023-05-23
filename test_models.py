import os
from unittest import TestCase
from flask_bcrypt import Bcrypt
from datetime import date

from models import db, connect_db, User, Trip, Location, Link, TripDay, Activity, DayActivity, UTripCamp, UTripAct

os.environ["DATABASE_URL"] = 'postgresql:///rec_trip_test'

bycrpt = Bcrypt()

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    
	def setUp(self):
		db.drop_all()
		db.create_all()

		test_user1 = User.signup("user1", "user1@test.com", "user1", "test", "testuser1234")
		db.session.commit()
	
	def tearDown(self):
		res = super().tearDown()
		db.session.rollback()
		return res
	
	def test_create_user(self):
		test_user2 = User.signup("user2", "user2@test.com", "user2", "test", "testuser2234")
		db.session.commit()

		test_user1 = User.query.get("user2")

		self.assertEqual(test_user1.username, "user2")

	def test_authenticate_user(self):
		user = User.authenticate("user1", "testuser1234")
		self.assertEqual(user.username, "user1")

class TripModelTestCase(TestCase):
	def setUp(self):
		db.drop_all()
		db.create_all()

		test_user1 = User.signup("user1", "user1@test.com", "user1", "test", "testuser1234")
		db.session.commit()

		test_trip = Trip.create_trip("test trip 1", date(2023, 6, 1), date(2023, 6, 5), "testing trip description", "user1")
	
	def tearDown(self):
		res = super().tearDown()
		db.session.rollback()
		return res
	
	def test_create_trip(self):
		new_trip = Trip.create_trip("test trip 2", date(2023, 7, 1), date(2023, 7, 5), "testing trip description 2", "user1")

		new_trip_days = TripDay.query.filter(TripDay.trip_id==new_trip.id).all()

		self.assertIsNot(new_trip.id, None)
		self.assertEqual(new_trip.name, "test trip 2")
		self.assertEqual(len(new_trip_days), 5)


