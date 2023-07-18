import requests, json, asyncio
from keys import REC_API_KEY, MAPS_KEY, TOMTOM_KEY
from datetime import timedelta, date, datetime

REC_BASE_URL = "https://ridb.recreation.gov/api/v1"
GEOCODE_BASE_URL = "https://api.tomtom.com/search/2/structuredGeocode.json"

######### ENDPOINTS ##############
ACTIVITIES = "activities"
CAMPSITES = "campsites"
EVENTS = "events"
FACILITIES = "facilities"
PERMIT = "permitentrances"
RECAREAS = "recareas"
TOURS = "tours"

def resource_search(endpoint, query="", limit="", offset="", full="true", state="", activity="", lat="", lon="", radius="", sort=""):
    
    """ multi purpose search of recreation.gov api """

    resp = requests.get(f"{REC_BASE_URL}/{endpoint}",
		params={
			"apikey" : REC_API_KEY,
			"query" : query,
			"limit" : limit,
			"offset" : offset,
			"full" : full,
			"state" : state,
			"activity" : activity,
			"latitude": lat,
			"longitude" : lon,
			"radius" : radius,
			"sort" : sort
		})
    return resp["RECDATA"].json()

def get_poi_by_activity_location(activity, lat, lon):
	facilities = resource_search(FACILITIES, 
                            	activity=activity, 
                                lat=lat, 
                                lon=lon,
                                full="false")
    
	recareas = resource_search(RECAREAS, 
								activity=activity, 
								lat=lat, 
								lon=lon,
								full="false")
	
	return make_poi_list(facilities, recareas)

def get_poi_by_activity_keyword(activity, keyword):
    facilities = resource_search(FACILITIES, 
                            	activity=activity,
                                keyword=keyword, 
                                full="false")
    recareas = resource_search(RECAREAS, 
                               	activity=activity,
                                keyword=keyword, 
                                full="false")
    
    return make_poi_list(facilities, recareas)

def clean_fac_search (data):
	return [
				{
					"id" : f"fac{f['FacilitiyID']}",
					"type" : "facility",
					"name" : f["FacilityName"],
					"city" : f["FACILITYADDRESS"][0]["City"],
					"state" : f["FACILITYADDRESS"][0]["AddressStateCode"]
				} 
            for f in data]
        
def clean_recarea_search (data):
   	return [
				{
					"id" : f"rec{r['RecAreaID']}",
					"type" : "recarea",
					"name" : r["RecAreaName"],
					"city" : r["RECAREAADDRESS"][0]["City"],
					"state" : r["RECAREAADDRESS"][0]["AddressStateCode"]
				} 
            for r in data]

def make_poi_list(facilities, recareas):
    facility_list = clean_fac_search(facilities)
    recarea_list = clean_recarea_search(recareas)
     
    return [*facility_list, *recarea_list]