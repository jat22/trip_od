from unittest import TestCase
from datetime import datetime

from helpers import Helpers

class HelpersTestCast(TestCase):

	def setup(self) -> None:
		return super().setUp()
	
	def tearDown(self) -> None:
		return super().tearDown()
	
	def test_generate_trip_dates(self):
		start_date = datetime(2023,9,1)
		end_date = datetime(2023,9,2)

		expected = [
			{
				"dow" : datetime(2023,9,1).strftime("%a"),
				"month" : datetime(2023,9,1).strftime("%b"),
				"day" : datetime(2023,9,1).strftime("%-d"),
				"year" : datetime(2023,9,1).strftime("%Y"),
				"id" : datetime(2023,9,1).strftime("%Y%m%d"),
				"datetime" : datetime(2023,9,1)
			},
			{
				"dow" : datetime(2023,9,2).strftime("%a"),
				"month" : datetime(2023,9,2).strftime("%b"),
				"day" : datetime(2023,9,2).strftime("%-d"),
				"year" : datetime(2023,9,2).strftime("%Y"),
				"id" : datetime(2023,9,2).strftime("%Y%m%d"),
				"datetime" : datetime(2023,9,2)
			}
		]

		result = Helpers.generate_trip_dates(start_date, end_date)

		self.assertEqual(result, expected)

	