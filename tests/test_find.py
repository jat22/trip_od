from unittest import TestCase
from datetime import date
from find import Find


class FindTestCase(TestCase):
    
	def setUp(self) -> None:
		return super().setUp()
	
	def tearDown(self) -> None:
		return super().tearDown()

	def test_parks(self):
		result = Find.parks("Alabama", "hiking")

		self.assertIsInstance(result, list)
		self.assertIn("park_code", result[0].keys())
		self.assertIn("name", result[0].keys())
		self.assertIn("description", result[0].keys())
		self.assertIn("lat", result[0].keys())

	def test_parks_by_state(self):
		result = Find.parks_by_state("Alabama")

		self.assertIsInstance(result, list)
		self.assertIn("park_code", result[0].keys())
		self.assertIn("name", result[0].keys())
		self.assertIn("description", result[0].keys())
		self.assertIn("lat", result[0].keys())

	def test_parks_by_term(self):
		result = Find.parks_by_term("Grand Canyon National Park")

		self.assertIsInstance(result, list)
		self.assertIn("park_code", result[0].keys())
		self.assertIn("name", result[0].keys())
		self.assertIn("description", result[0].keys())
		self.assertIn("lat", result[0].keys())

	def test_park_details(self):
		result = Find.park_details("grca")

		self.assertIsInstance(result, dict)
		self.assertIn("images", result.keys())
		self.assertIn("campgrounds", result.keys())
		self.assertIsInstance(result["campgrounds"], list)