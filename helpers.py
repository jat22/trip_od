from datetime import timedelta

class Helpers:
	@classmethod
	def generate_trip_dates(cls, start, end):
		"""given a start date and an end date (as datetime objects), a list of date dictionaries in that range are returned"""
		
		date_range = cls.make_date_range(start,end)
		trip_dates = [cls.make_date_dict(date) for date in date_range]
		return trip_dates

	@classmethod
	def make_date_range(cls, start, end):
		date_range = [start + timedelta(days = x) for x in range((end-start).days + 1)]
		return date_range
	
	@classmethod
	def make_date_dict(cls, date):
		""" given a datatime object, a dictionary of with data information is
			returned in a format that is usable for display purposes."""
		
		date_dict = {
			"dow" : date.strftime("%a"),
			"month" : date.strftime("%b"),
			"day" : date.strftime("%-d"),
			"year" : date.strftime("%Y"),
			"id" : date.strftime("%Y%m%d"),
			"datetime" : date
		}
		return date_dict