import os, subprocess
from unittest import TestCase
import datetime
import forms
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
	
	def test_signup_get(self):
		with self.client as c:
			resp = c.get('users/new')
			html = resp.get_data(as_text=True)

			self.assertEqual(resp.status_code, 200)

	def test_signup_post(self):
		with self.client as c:
			form = forms.CreateAccountForm()
			form.username.data = "createTest1"
			form.email.data = "test@create.com"
			form.first_name.data = "CreateMe"
			form.last_name.data = "TESTING"
			form.password.data = "abc123456"

			res = c.post('users/new', data=form.data)

			new_user = User.query.get("createTest1")

			self.assertEqual(res.status_code, 302)
			self.assertEqual(new_user.username, "createTest1")

	def test_show_a_trip(self):
		with self.client as c:
			with c.session_transaction() as sess:
				sess[CURR_USER] = "user1"
				trip = Trip.query.filter(Trip.name=="Smoky Mountains").first()
				sess[CURR_TRIP] = trip.id

			res = c.get(f"/trips/{trip.id}")
			html = res.get_data(as_text=True)

			self.assertEqual(res.status_code, 200)
			self.assertIn("Smoky Mountains", html)

	def test_create_trip(self):
		with self.client as c:
			with c.session_transaction() as sess:
				sess[CURR_USER] = "user1"
			
			form = forms.CreateTripForm()
			form.name.data = "Test Trip1"
			form.start_date.data = "2023-06-30"
			form.end_date.data = "2023-07-04"
			form.description.data = "testing 123, testing 123"

			res = c.post("trips/create", data=form.data)

			newTrip = Trip.query.filter(Trip.name=="Test Trip1").first()

			self.assertEqual(res.status_code, 302)
			self.assertEqual(newTrip.name, "Test Trip1")

	def test_show_activity_options(self):
		with self.client as c:
			with c.session_transaction() as sess:
				sess[CURR_USER] = "user1"
				trip = Trip.query.filter(Trip.name=="Smoky Mountains").first()
				sess[CURR_TRIP] = trip.id

			res = c.get(f"/trips/{trip.id}/activities")

			self.assertEqual(res.status_code, 200)

	# def test_login_exists(self):
	# 	with self.client as c:
	# 		with c.session_transaction() as sess:
	# 			sess[CURR_USER] = None

	# 			resp = c.post("/login", data = {"username" : "user1", "password": "user12345"})

	# 			self.assertEqual(sess[CURR_USER], "user1")
		