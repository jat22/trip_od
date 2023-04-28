# from flask import Flask, redirect, render_template, jsonify
# from flask_debugtoolbar import DebugToolbarExtension
import requests, json, asyncio
from keys import REC_API_KEY, MAPS_KEY, TOMTOM_KEY

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



################# REC API SEARCH ############################
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
    
    campgrounds = filter_campgrounds(facilities)

    return {"activities": activities, "campgrounds" : campgrounds}




############################### FILETER AND CLEAN #########################
def filter_campgrounds(facilities):
    campgrounds = [fac for fac in facilities 
                   if fac["FacilityTypeDescription"] == "Campground"]
    clean_campgrounds = clean_resources("Facility", campgrounds)
    return clean_campgrounds

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