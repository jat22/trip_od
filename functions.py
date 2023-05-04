# from flask import Flask, redirect, render_template, jsonify
# from flask_debugtoolbar import DebugToolbarExtension
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



################# REC API SEARCH FUNCTIONS ############################
def resource_search(endpoint, query="", limit="", offset="", full="true", state="", activity="", lat="", long="", radius="", sort=""):
    
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
			"longitude" : long,
			"radius" : radius,
			"sort" : sort
		})
    return resp.json()

def location_detail_search(location_id):
    api_type = location_id[:3]
    api_id = location_id[3:]

    if api_type == "fac":
        endpoint = FACILITIES
        type = "Facility"
    if api_type == "rec":
        endpoint = RECAREAS
        type = "RecArea"

    resp = requests.get(f"{REC_BASE_URL}/{endpoint}/{api_id}",
        params={"apikey" : REC_API_KEY, "full" : "true"})
    
    return {"type" : type, "data" : resp.json()}



######################### TOMTOM API GEOLOCATION SEARCH #######################
def geolocation_search(city, state):
    resp = requests.get(f"{GEOCODE_BASE_URL}",
                        params = {
                            "key" : TOMTOM_KEY,
                            "countryCode" : "US",
                            "municipality" : city,
                            "countrySubdivision" : state,
							"entityTypeSet" : "Municipality"
                        })
    return resp.json()

def get_coordinates(city, state):
    data = geolocation_search(city, state)
    coordinates = [result.get("position") for result in data.get("results")]
    return coordinates




############################ MAIN SEARCH FUNCTION ###########################
def search_by_location(city, state, latitude, longitude, radius="50"):
    lat = latitude
    long = longitude
    if not lat and not long:
        coords = get_coordinates(city, state)
        lat = coords[0].get("lat")
        long = coords[0].get("lon")
    
    activities_campgrounds = get_activities_campgrounds(lat, long, radius)

    results = {
        		"search_geolocation" : {"lat" : lat, "long" : long},
                "activities" : activities_campgrounds["activities"],
                "campgrounds" : activities_campgrounds["campgrounds"]
	}

    return results

def get_location_details(location_id):
    data = location_detail_search(location_id)
    details = clean_location_data(data)
    
    return details
        

######################## SEARCH HELPERS ##################################    
def get_activities_campgrounds(lat, long, radius):
    
    facilities = resource_search(FACILITIES, lat=lat, long=long, radius=radius)["RECDATA"]
    clean_facilities = clean_resources("Facility", facilities)

    recareas = resource_search(RECAREAS, lat=lat, long=long, radius=radius)["RECDATA"]
    clean_recareas = clean_resources("RecArea", recareas)

    locations = clean_facilities + clean_recareas

    activity_names = []
    for loc in locations:
        for act in loc["activities"]:
            activity_names.append(act)
    unique_activity_names = list(set(activity_names))
	
    activities = [{"name" : act, "locations" : []} for act in unique_activity_names]
    
    for act in activities:
        for loc in locations:
            for loc_act in loc["activities"]:
                if loc_act == act["name"]:
                    act["locations"].append(loc)
    
    campgrounds = filter_campgrounds(locations)

    return {"activities": activities, "campgrounds" : campgrounds}




############################### FILETER AND CLEAN #########################
def filter_campgrounds(facilities):
    print(facilities)
    campgrounds = [fac for fac in facilities 
                   if "CAMPING" in fac["activities"]]
    return campgrounds

def clean_resources(type, resource_list):
    if type == "Facility":
        typ_abr = "fac"
    if type == "RecArea":
        typ_abr = "rec"

    resources = [{
        "id" : typ_abr + res[f"{type}ID"],
        "name" : res[f"{type}Name"],
        "lat" : res[f"{type}Latitude"],
        "long" : res[f"{type}Longitude"],
        "activities" : [act["ActivityName"] for act in res["ACTIVITY"]]
		}
    	for res in resource_list]
    
    return resources

def clean_location_data(resp_data):
    type = resp_data["type"]
    data = resp_data["data"]
    
    if type == "Facility" :
        id_type = "fac"
    if type == "RecArea" :
        id_type = "rec"

    details = {
        "id" : id_type + data[f"{type}ID"],
    	"name" : data[f"{type}Name"],
        "email" : data[f"{type}Email"],
        "phone" : data[f"{type}Phone"],
        "description" : data[f"{type}Description"],
        "directions" : data[f"{type}Directions"],
        "address" : data.get(f"{type.upper()}ADDRESS")[0][f"{type}StreetAddress1"],
        "city" : data.get(f"{type.upper()}ADDRESS")[0]["City"],
        "state" : data.get(f"{type.upper()}ADDRESS")[0]["AddressStateCode"],
        "zip" : data.get(f"{type.upper()}ADDRESS")[0]["PostalCode"],
        "lat" : data[f"{type}Latitude"],
        "long" : data[f"{type}Longitude"],
        "links" : [{"title" : link["Title"], 
                    "url" : link["URL"],
                    "location" : id_type + data[f"{type}ID"]} 
                    for link in data["LINK"]]
	}
    return details


def make_date_dict(date):
    date_dict = {
        "dow" : date.strftime("%a"),
        "month" : date.strftime("%b"),
        "day" : date.strftime("%-d"),
        "year" : date.strftime("%Y"),
        "id" : date.strftime("%Y%m%d"),
        "datetime" : date
    }
    return date_dict

def trip_dates(start, end):
    date_range = [start + timedelta(days = x) for x in range((end-start).days + 1)]

    trip_dates = [make_date_dict(date) for date in date_range]

    return trip_dates



################# GET ALL ACTIVITIES ####################

def get_all_activities():
    data = resource_search("activities")["RECDATA"]
    return name_id_only(data, "Activity")

def name_id_only(list, type):

    info = [{
		"id" : data.get(f"{type}ID"), 
		"name" : data.get(f"{type}Name").lower()
		} 
		for data in list]
    return info