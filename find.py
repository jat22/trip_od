import requests
from keys import NPS_KEY
from states import state_names

NPS_BASE_URL = "https://developer.nps.gov/api/v1"

class Find:
	@classmethod
	def parks(cls, state, term):

		resp = requests.get(f"{NPS_BASE_URL}/parks",
		    	params = {
					"api_key" : NPS_KEY,
					"stateCode" : state_names.get(state),
					"q" : term
				}
			)
		data = resp.json()

		return Format.search_results(data)
	
	@classmethod
	def parks_by_state(cls, state):

		resp = requests.get(f"{NPS_BASE_URL}/parks",
		    	params = {
					"api_key" : NPS_KEY,
					"stateCode" : state_names.get(state),
				}
			)
		data = resp.json()

		return Format.search_results(data)
	
	@classmethod
	def parks_by_term(cls, term):

		resp = requests.get(f"{NPS_BASE_URL}/parks",
		    	params = {
					"api_key" : NPS_KEY,
					"q" : term
				}
			)
		data = resp.json()

		return Format.search_results(data)
	
	@classmethod
	def park_details(cls, park_code):
		park_resp = requests.get(f"{NPS_BASE_URL}/parks",
			   params = {
				   "api_key" : NPS_KEY,
				   "parkCode" : park_code
			   }
		)
		park_data = park_resp.json()

		things_resp = requests.get(f"{NPS_BASE_URL}/thingstodo",
			     params = {
				     "api_key" : NPS_KEY,
				     "parkCode" : park_code
				 }
		)
		things_data = things_resp.json()

		campgrounds_resp = requests.get(f"{NPS_BASE_URL}/campgrounds",
			     params = {
				     "api_key" : NPS_KEY,
				     "parkCode" : park_code
				 })
		
		campgrounds_data = campgrounds_resp.json()

		return Format.park_details(park_data, things_data, campgrounds_data)
	
class Format:
	@classmethod
	def search_results(cls, resp):
		parks = resp["data"]
		results = [
            {
				"park_code" : p.get("parkCode"),
				"name" : p.get("fullName"),
				"description" : p.get("description"),
				"lat" : p.get("latitude"),
				"lon" : p.get("longitude"),
				"activities" : [a.get("name") for a in p.get("activities")],
				"states" : [s.strip() for s in p.get("states").split(',')],
				"image" : p.get("images")[0] if len(p.get("images")) > 0 else None
			} for p in parks]
		
		return results
	
	@classmethod
	def park_details(cls, park, things, campgrounds):
		park = park["data"][0]
		things = things["data"]
		campgrounds = campgrounds["data"]
		details = {
			"park_code" : park.get("parkCode"),
			"name" : park.get("fullName"),
			"description" : park.get("description"),
			"url" : park.get("url"),
			"lat" : park.get("latitude"),
			"lon" : park.get("longitude"),
			"states" : park.get("states"),
			"images" : park.get("images"),
			"contact" : park.get("contacts"),
			"address" : [a for a in park.get("addresses") 
					if a.get("type") == "Physical"
				][0],
			"activities" : [a.get("name") for a in park.get("activities")],
			"things_to_do" : [
				{
					"id" : t.get("id"),
					"title" : t.get("title"), 
					"url" : t.get("url"), 
					"desc" : t.get("shortDescription"),
					"image" : t.get("images")[0].get("url")
				} 
					for t in things
   				],
			"campgrounds" : [
				{
					"id" : c.get("id"),
					"name" : c.get("name"),
					"url" : c.get("url"),
					"description" : c.get("description"),
					"lat" : c.get("latitude"),
					"lon" : c.get("longitude"),
					"reserve_url" : c.get("reservationUrl"),
					"phone" : c.get("contacts").get("phoneNumbers")[0] 
								if len(c.get("contacts").get("phoneNumbers")) > 0
								else None,
					"email" :  c.get("contacts").get("emailAddresses")[0] 
								if len(c.get("contacts").get("emailAddresses")) > 0
								else None
				}
					for c in campgrounds
					if len(campgrounds) > 0
				]
		}

		return details