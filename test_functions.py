
from unittest import TestCase
from datetime import date
import functions


class FunctionTestCase(TestCase):
    
	def setUp(self) -> None:
		return super().setUp()
	
	def tearDown(self) -> None:
		return super().tearDown()

	def test_resource_search(self):
		resp = functions.resource_search("facilities", lat="40.7608", long="-111.8910")

		self.assertIsInstance(resp, dict)

	def test_location_detail_search(self):
		resp = functions.location_detail_search("fac1234")

		self.assertEqual(resp["type"], "Facility")
		self.assertIsInstance(resp["data"], dict)

	def test_geolocation_searhc(self):
		resp = functions.geolocation_search("Salt Lake City", "Utah")

		self.assertIsInstance(resp, dict)

	def test_get_coordinates(self):
		cords = functions.get_coordinates("Salt Lake City", "Utah")
		
		self.assertIsInstance(cords, list)

	def test_search_by_location(self):
		results = functions.search_by_location("Salt Lake City", "Utah", "", "")

		self.assertIn("search_geolocation", results)
		self.assertIsInstance(results["activities"], list)
		self.assertIsInstance(results["campgrounds"], list)

	def test_get_location_details(self):
		details = functions.get_location_details('fac232478')

		self.assertEqual(len(details), 13)
		self.assertIn("name", details)
		self.assertIn("description", details)
		self.assertIsInstance(details["links"], list)

	def test_get_activities_campgrounds(self):
		results = functions.get_activities_campgrounds('35.4627778', '-83.4344444', '')

		self.assertIn("activities", results)
		self.assertIn("campgrounds", results)
		self.assertEqual(len(results), 2)

	

	def test_make_date_dict(self):
		date_dict = functions.make_date_dict(date(2023, 6, 1))

		self.assertEqual(len(date_dict), 6)
		self.assertIsInstance(date_dict, dict)
		self.assertEqual(date_dict["id"], "20230601")
		self.assertEqual(date_dict["month"], "Jun")