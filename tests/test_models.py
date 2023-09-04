import os
from unittest import TestCase
from unittest.mock import Mock, patch
from datetime import datetime

from models import db, connect_db, User, Park, Trip, Campground, ThingToDo, TripDay, DayThingsToDo
from find import Find

os.environ["DATABASE_URL"] = "postgresql:///adventurely-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
	def setUp(self):
		db.drop_all()
		db.create_all()

		test_user1 = User.signup("testuser1", "test1@user.com", "Test1", "User1", "password")

		db.session.commit()

	def tearDown(self):
		res = super().tearDown()
		db.session.rollback()
		return res
	
	def test_signup(self):
		testuser2 = User.signup("testuser2", "test2@user.com", "Test2", "User2", "password")

		db.session.commit()

		user = User.query.get("testuser2")

		self.assertEqual(user.username, "testuser2")
		self.assertTrue(user.password.startswith('$2b$'))

	def test_authenticate(self):
		user_correct = User.authenticate("testuser1", "password")
		user_incorrect = User.authenticate("testuser1", "notcorrect")

		self.assertEqual(user_correct.username, "testuser1")
		self.assertFalse(user_incorrect)

class ParkModelTestCase(TestCase):
	def setUp(self):
		db.drop_all()
		db.create_all()

	def tearDown(self):
		res = super().tearDown()
		db.session.rollback()
		return res
	
	@patch('find.Find.park_details')
	def test_create(self, mock_park_details):
		mock_park_data = {
			"name" : "Test Park",
			"url" : "www.park.com",
			"lat" : "111.222",
			"lon" : "-45.234",
			"things_to_do" : [{
				"id" : "thing1",
				"park_code" : "tstp",
				"title" : "test thing",
				"url" : "www.thing.test"
			}],
			"campgrounds" : [{
				"id" : "123",
				"name" : "test campground",
				"url" : "www.camping.com",
				"lat" : "123.123",
				"lon" : "-123",
				"park_code" : "tstp"
			}]
		}

		mock_park_details.return_value = mock_park_data

		Park.create("tstp")

		park = Park.query.get("tstp")

		self.assertEqual(park.name, "Test Park")
		self.assertEqual(len(park.campgrounds), 1)
		self.assertEqual(len(park.things_to_do), 1)

class TripTestCase(TestCase):
	def setUp(self):
		db.drop_all()
		db.create_all()

		test_user1 = User.signup("testuser1", "test1@user.com", "Test1", "User1", "password")

		db.session.commit()

	def tearDown(self):
		res = super().tearDown()
		db.session.rollback()
		return res

	@patch('find.Find.park_details')
	def test_create(self, mock_park_details):
		mock_park_data = {
			"name" : "Test Park",
			"url" : "www.park.com",
			"lat" : "111.222",
			"lon" : "-45.234",
			"things_to_do" : [{
				"id" : "thing1",
				"park_code" : "tstp",
				"title" : "test thing",
				"url" : "www.thing.test"
			}],
			"campgrounds" : [{
				"id" : "123",
				"name" : "test campground",
				"url" : "www.camping.com",
				"lat" : "123.123",
				"lon" : "-123",
				"park_code" : "tstp"
			}]
		}

		mock_park_details.return_value = mock_park_data

		trip = Trip.create(datetime(2023,9,1), datetime(2023,9,5), "testuser1", "tstp")

		self.assertTrue(trip)
