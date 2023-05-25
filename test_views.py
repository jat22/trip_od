import os, subprocess
from unittest import TestCase

from models import connect_db, db, User, Trip, Location, TripDay, DayActivity, UTripAct, UTripCamp, bcrypt, Activity

os.environ["DATABASE_URL"] = 'postgresql:///rec_trip_test'

from app import app, CURR_USER, CURR_TRIP, do_login

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):
    
	def setUp(self):
		self.client = app.test_client()

		seed_file = 'seed.py'
		subprocess.run(['python', seed_file])

	def tearDown(self):
		resp = super().tearDown()
		db.session.rollback()
		return resp
	
	def test_login_exists(self):
		with self.client as c:
			with c.session_transaction() as sess:
				sess[CURR_USER] = None

				resp = c.post("/login", data = {"username" : "user1", "password": "user12345"})

				self.assertEqual(sess[CURR_USER], "user1")
		