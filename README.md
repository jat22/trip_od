## Adventure Outdoors 
https://adventureod.onrender.com/ </br>
Simple tool to plan camping trips in national parks and recreation areas.

### Features:
- Create a user account.
- Create a trip and save to user account.
- Get information about campgrounds available at particular locations
- Get information about activities available at particular locations.

### Walk-thru
On the landing page, either log-in or create an account. Once logged in you will see your saved trips. To create a new trip, click on the "Plan A New Adventure" button. You will enter a title for your trip, start date, end date and an optional description. Submitting this information will create a new trip instance and direct you to pick a geographical location for your trip (search by either city/state or lat/long). After submitting this search a list of campgrounds near that location will be provided. You can link to each campground to get more information and add campgrounds you are interested in to your trip by clicking the "Add to Trip" button. You can then either go directly to your trip details page by click the "Go to Trip" button or find activities. When viewing activities, you will see a list of activities available, clicking on one will take you to a list of locations where you can do this activity. You can add the activity to your trip and it is tied to that particular location.

On the trip details page you can see the campgrounds and activities that you have selected. From there you can assign these to particular days of your trip. Or delete them entirely from the the current trip. If you would like to find more campgrounds or activites, follow the appropriate links on the right side of the page. To edit the trip dates or title click the edit button at the top of the page.

### APIs:
Recreation.gov: https://ridb.recreation.gov/docs#/</br>
All data comes from recreation.gov's api. </br>
TomTom: https://developer.tomtom.com/search-api/api-explorer </br>
Latitude and longitude information is gathered from tomtom. Future features will also include maps from tomtom's api.

### Stack:
- Python/Flask (including jinja, wtforms)
- Postgres
- SQLAlchemy
- Bootstrap
- HTML/CSS/Javascript