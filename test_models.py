import os
from unittest import TestCase
from datetime import date

from models import db, connect_db, User, Trip, Location, TripDay

os.environ["DATABASE_URL"] = 'postgresql:///rec_trip_test'

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

	def test_create_location(self):
		location = Location.create_location('rec1234', "Test Location", "123-456-7890", "location@test.com", "This is a test location.", "Turn left at test location dr and continue on until morning.", "1234 Test Rd", "A City", "SomeState", "11111", "12.12345", "-123.1234", [{"title" : "test-link1", "url" : "http://this.test1.com", "location_id" : 'rec1234'}, {"title" : "test-link2", "url" : "http://this.test2.com", "location_id" : 'rec1234'}])

		self.assertIsNot(location.id, None)
		self.assertEqual(location.name, "Test Location")
		self.assertEqual(len(location.links), 2)


class TripDayTestCase(TestCase):
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
	
	def test_add_tripday(self):
		trip = Trip.query.filter(Trip.name=="test trip 1").first()
		new_days = TripDay.add(date(2023, 5, 30), date(2023, 5, 31), trip.id)
		all_days = TripDay.query.order_by(TripDay.date).all()

		self.assertEqual(len(trip.days), 7)
		self.assertEqual(all_days[0].date, date(2023, 5, 30))
		self.assertEqual(all_days[-1].date, date(2023, 6, 5))