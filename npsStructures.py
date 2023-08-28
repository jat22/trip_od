

########### FOR SEARCH RESULTS ###########
# /parks; q or state
p = {}
park = {
    "parkCode" : p.get("parkCode"),
    "name" : p.get("name"),
    "description" : p.get("description"),
    "lat" : p.get("latitude"),
    "long" : p.get("longitude"),
    "activities" : [a.get("name") for a in p.get("activities")],
    "states" : p.get("states"),
    "image" : p.get("images")[0]
}


############ PARK DETAIL PAGE #################
# /parks; parkCode
p={}
# /thingstodo; parkCode
ttd = {}

park = {
	"park_code" : p.get("parkCode"),
    "name" : p.get("name"),
    "designation" : p.get("designation"),
    "description" : p.get("description"),
    "url" : p.get("url"),
    "lat" : p.get("latitude"),
    "lon" : p.get("longitude"),
    "activities" : p.get("activities"),
    "states" : p.get("states"),
    "images" : p.get("images"),
    "contact" : p.get("contacts"),
    "direction_url" : p.get("directionsUrl"),
    "address" : [a for a in p.get("addresses") if a.get("type") == "Physical"],
    "things_to_do" : [
        {
            "id" : t.get("id")
			"title" : t.get("title"), 
         	"url" : t.get("url"), 
         	"desc" : t.get("shortDescription"),
            "image" : t.get("images")[0].get("url")
        } for t in ttd
    ],
}

############# PARK DATA FOR DB ##############
class Park(db.Model):
    __tablename__ = "parks"
    
    id = park.get("park_code")
    name = park.get("name")
    lat = park.get("lat")
    lon = park.get("lon")


############# CAMPGROUND DETAILS ############
cg = {}

campground = {
    "id" : cg.get("id"),
    "name" : cg.get("name"),
    "park_code" : cg.get("parkCode"),
    "url" : cg.get("url"),
    "description" : cg.get("description"),
    "lat" : cg.get("lat"),
    "lon" : cg.get("lon"),
    "reservation_url" : cg.get("reservationUrl"),
    "address" : [c for c in cg.get("addresses") if c.get("type") == "Physical"],
    "images" : cg.get("images"),
    "classification" : cg.get("classification")
}

############## CAMPGROUND DATA DB ############

class Campground(db.Model):
	__tablename__ = "campgrounds"
    
	id = campground.get("id")
	name = campground.get("name")
	url = campground.get("url")
	lat = campground.get("lat")
	lon = campground.get("lon")
