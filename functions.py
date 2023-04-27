# from flask import Flask, redirect, render_template, jsonify
# from flask_debugtoolbar import DebugToolbarExtension
import requests, json, asyncio
from keys import REC_API_KEY, MAPS_KEY, TOMTOM_KEY

REC_BASE_URL = "https://ridb.recreation.gov/api/v1"
GEOCODE_BASE_URL = "https://api.tomtom.com/search/2/structuredGeocode.json"
ACTIVITIES = "activities"
CAMPSITES = "campsites"
EVENTS = "events"
FACILITIES = "facilities"
PERMIT = "permitentrances"
RECAREAS = "recareas"
TOURS = "tours"


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

def activities_with_parent_resources_by_location(location_type, city="", state=""):
    coords = get_coordinates(location_type, city, state)
    lat = coords[0].get('lat')
    long = coords[0].get('lon')

    recareas = min_data(resource_search(RECAREAS, lat=lat, long=long)["RECDATA"], "RecArea")
    facilities = min_data(resource_search(FACILITIES, lat=lat, long=long)["RECDATA"], "Facility")

    fac_rec_data = recareas + facilities
    print(fac_rec_data)
    fac_rec_activities =[]
    all_activities_dict = {}

    for fac_rec in fac_rec_data:
        for activity in fac_rec["activities"]:
            fac_rec_activities.append(activity)


    for a in fac_rec_activities:
        name = a["name"]
        id = a["id"]
        parent_type = a["parent_type"]
        parent_id = a["parent_id"]
        parent_name = a["parent_name"]

        if name not in all_activities_dict:
            all_activities_dict[name] = ({"name" : name, "id" : id, "type" : "activity",
                                    "parents" : [{"type" : parent_type, "id" : parent_id, "name" : parent_name}]})
        else:
            all_activities_dict[name]['parents'].append({"type" : parent_type, "id" : parent_id, "name" : parent_name})

    all_activites_parents = [all_activities_dict[act] for act in all_activities_dict]

    print(all_activites_parents)

    return all_activites_parents


def geolocation_search(city="", state="", zip=""):
    resp = requests.get(f"{GEOCODE_BASE_URL}",
                        params = {
                            "key" : TOMTOM_KEY,
                            "countryCode" : "US",
                            "municipality" : city,
                            "countrySubdivision" : state,
                            "postalCode" : zip
                        })
    return resp.json()

def get_coordinates(search_type, city="", state="", zip=""):
    data = geolocation_search(city, state, zip)
    if search_type == "city-state":
        coordinates = [result.get('position') for result in data.get("results")
            if result.get('entityType') == "Municipality"]
        return coordinates
    if search_type == "zip":
        coordinates = [result.get('position') for result in data.get("results")
            if result.get('entityType') == "PostalCodeArea"]
        return coordinates

def min_data(data, type):
    rec_areas = data
    clean_rec_areas = [{
        "name" : area.get(f"{type}Name"),
        "id" : area.get(f"{type}ID"),
        "activities" : clean_activities(
            area.get("ACTIVITY"), type, area.get(f"{type}ID"), area.get(f"{type}Name")),
        }
        for area in rec_areas]
    return clean_rec_areas

def clean_activities(list, parentType, parentID, parentName):
    activities = [{
		"name" : data.get("ActivityName").lower(),
        "id" : data.get("ActivityID"),
        "parent_type" : parentType,
        "parent_id" : parentID,
        "parent_name" : parentName
        }
        for data in list]
    return activities