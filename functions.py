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
    return resp.json()["RECDATA"]

def location_detail_search(location_id):

    """ location (facility or recarea) search of api """

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
    """ given a city/state, TomTom api is searched for location information"""

    resp = requests.get(f"{GEOCODE_BASE_URL}",
                        params = {
                            "key" : TOMTOM_KEY,
                            "countryCode" : "US",
                            "municipality" : city,
                            "countrySubdivision" : state,
							"entityTypeSet" : "Municipality"
                        })
    


    return resp.json().get("results")

def get_location_options(city, state):
    """ given a city and state, lat/long coordinates are returned."""

    data = geolocation_search(city, state)

    location_options = [
        {
            "city" : city.get("address").get("municipality"), 
            "state" : city.get("address").get("countrySubdivision"), 
            "cords" : 
            {
                "lat" : city.get("position").get("lat"), 
                "lon" : city.get("position").get("lon")
            }
        } 
        for city in data]

    return location_options




############################ MAIN SEARCH FUNCTION ###########################

def search_by_location(activity, lat, lon):
	facilities = resource_search(FACILITIES, 
                            	activity=activity, 
                                lat=lat, 
                                lon=lon,
                                full="true")
    
	recareas = resource_search(RECAREAS, 
								activity=activity, 
								lat=lat, 
								lon=lon,
								full="true")
	
	return make_poi_list(facilities, recareas)

def search_by_poi(activity, keyword):
    facilities = resource_search(FACILITIES, 
                            	activity=activity,
                                query=keyword, 
                                full="true")
    recareas = resource_search(RECAREAS, 
                               	activity=activity,
                                query=keyword, 
                                full="true")
    
    return make_poi_list(facilities, recareas)

def clean_fac_search (data):
    return [
				{
					"id" : f"fac{f['FacilityID']}",
					"type" : f["FacilityTypeDescription"],
					"name" : f["FacilityName"],
					"city" : f["FACILITYADDRESS"][0].get("City") if len(f["FACILITYADDRESS"]) > 0 else None,
					"state" : f["FACILITYADDRESS"][0].get("AddressStateCode") if len(f["FACILITYADDRESS"]) > 0 else None,
				} 
            for f in data]
        
def clean_recarea_search (data):
   	return [
				{
					"id" : f"rec{r['RecAreaID']}",
					"type" : "Recreation Area",
					"name" : r["RecAreaName"],
					"city" : r["RECAREAADDRESS"][0].get("City") if len(r["RECAREAADDRESS"]) > 0 else None,
					"state" : r["RECAREAADDRESS"][0].get("AddressStateCode") if len(r["RECAREAADDRESS"]) > 0 else None
				} 
            for r in data]

def make_poi_list(facilities, recareas):
    facility_list = clean_fac_search(facilities)
    recarea_list = clean_recarea_search(recareas)
     
    return [*facility_list, *recarea_list]


# def search_by_location(city, state, latitude, longitude, radius="50"):
#     """ give geo location information, cleaned data about acitivities and campgrounds returned"""

#     lat = latitude
#     long = longitude
#     if not lat and not long:
#         coords = get_coordinates(city, state)
#         lat = coords[0].get("lat")
#         long = coords[0].get("lon")
    
#     activities_campgrounds = get_activities_campgrounds(lat, long, radius)

#     results = {
#         		"search_geolocation" : {"lat" : lat, "long" : long, "radius" : radius},
#                 "activities" : activities_campgrounds["activities"],
#                 "campgrounds" : activities_campgrounds["campgrounds"]
# 	}

#     return results

def get_poi_details(location_id):
    """ given a specific location (facility or recarea) id, cleaned data is returned"""
    data = location_detail_search(location_id)
    details = clean_location_data(data)
    
    return details
        

######################## SEARCH HELPERS ##################################    
def get_activities_campgrounds(lat, long, radius):
    """ given geo location data, activity and campground data is returned in a dicitonary"""
    facilities = resource_search(FACILITIES, lat=lat, long=long, radius=radius)["RECDATA"]
    clean_facilities = clean_resources("Facility", facilities)

    recareas = resource_search(RECAREAS, lat=lat, long=long, radius=radius)["RECDATA"]
    clean_recareas = clean_resources("RecArea", recareas)

    locations = clean_facilities + clean_recareas

    activity_ids = []
    for loc in locations:
        for act in loc["activities"]:
            activity_ids.append(act["id"])
    unique_activity_ids = list(set(activity_ids))


	
    activities = [{"id": id, "name" : "", "locations" : []} for id in unique_activity_ids]
    


    for act in activities:
        for loc in locations:
            for loc_act in loc["activities"]:
                if loc_act["id"] == act["id"]:
                    act["name"] = loc_act["name"]
                    act["locations"].append(loc)
    
    campgrounds = filter_campgrounds(locations)

    return {"activities": activities, "campgrounds" : campgrounds}




############################### FILTER AND CLEAN #########################
def filter_campgrounds(facilities):
    """ given a list of facilities, a list of campgrounds is returned;
        (all campgrounds are facilities, all facilities are not campgrounds)
    """

    campgrounds = []

    for fac in facilities:
        for act in fac["activities"]:
            if act["id"] == 9:
                campgrounds.append(fac)

    return campgrounds

def clean_resources(type, resource_list):
    """ given a list of resources, of a particular type (facility or recarea)
        a list with cleaned data is returned
    """
    if type == "Facility":
        typ_abr = "fac"
    if type == "RecArea":
        typ_abr = "rec"

    resources = [{
        "id" : typ_abr + res[f"{type}ID"],
        "name" : res[f"{type}Name"].title(),
        "lat" : res[f"{type}Latitude"],
        "long" : res[f"{type}Longitude"],
        "activities" : [{"id": act["ActivityID"], "name" : act["ActivityName"].title()} for act in res["ACTIVITY"]]
		}
    	for res in resource_list]
    
    return resources

def clean_location_data(resp_data):
    """give data on a single location (facility or recarea), clean data is returned"""

    type = resp_data["type"]
    data = resp_data["data"]
    
    if type == "Facility" :
        details = {
            "id" : "fac" + data[f"{type}ID"],
            "name" : data[f"{type}Name"].title(),
            "type" : "facility",
            "subtype" : data["FacilityTypeDescription"],
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
                        "location_id" : "fac" + data[f"{type}ID"]} 
                        for link in data["LINK"]],
            "pic" : data["MEDIA"][0]["URL"] if len(data["MEDIA"]) > 0 else "",
            "activities" :[act["ActivityName"] for act in data["ACTIVITY"]]
	    }


    if type == "RecArea" :
        details = {
            "id" : "rec" + data[f"{type}ID"],
            "name" : data[f"{type}Name"].title(),
            "type" : "recarea",
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
                        "location_id" : "fac" + data[f"{type}ID"]} 
                        for link in data["LINK"]],
            "pic" : data["MEDIA"][0]["URL"] if len(data["MEDIA"]) > 0 else "",
            "activities" :[act["ActivityName"] for act in data["ACTIVITY"]]
        }

    print("#################################")
    print(details)
    return details


def make_date_dict(date):
    """ given a datatime object, a dictionary of with data information is returned in 
        a format that is usable for display purposes.
    """
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
    """given a start date and an end date (as datetime objects), a list of date dictionaries in that range are returned"""

    date_range = make_date_range(start,end)

    trip_dates = [make_date_dict(date) for date in date_range]

    return trip_dates

def make_date_range(start, end):
    date_range = [start + timedelta(days = x) for x in range((end-start).days + 1)]
    return date_range

def get_all_activities():
    """ retreives a list of all activities from recreation.gov api """

    data = resource_search("activities")["RECDATA"]
    return name_id_only(data, "Activity")

def name_id_only(list, type):
    """ cleaning helper function that given a list of resources, it returns only the name and id of those resources.
    """

    info = [{
		"id" : data.get(f"{type}ID"), 
		"name" : data.get(f"{type}Name").title()
		} 
		for data in list]
    return info

def display_date(date):
    """ given a datatime object, returns a date as Month, day,"""
    return date.strftime("%b %-d, %Y")
