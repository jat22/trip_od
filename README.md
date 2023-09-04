## Adventurely
Simple tool for planning trips to National Park Service lands in the United States. Browse parks by state or search for a park name or keyword.

## Features
- Explore parks and what they have to offer.
- Create a user account so that you can create a trip itinerary for a particular park.
- Add a campground for each day of your trip
- Add things to do to each day of your trip

## Landing Page
This is a simple search page. Select a state where you would like to explore parks and/or enter a keyword or park name.

## Search Results
Displays a list of search results with some basic information about each result. At the top of the page you can enter new information and update search results.

## Park Details Page
Further details about a park including campgrounds, activities and things to do. This page contains external links to the park'ss official webpage and a link to the location on Google Maps. If you are logged in there is a button at the top of the page to create a trip to the park. If you are not logged in there are links to do so.

## Trip Details Page
The left side of this page is your trip itinerary and the right side contains a list of avaliable campgrounds and things to do. On each of these lists, you can link to more information about the particular resource. You can also select a day, click add and that thing to do or campground will be added to that particular day on your itenerary.

## My Trips
This page shows a list of a trips that the user has planned. You can click on any of the trips and get to the Trip Details Page.

## API and Stack:
The data utilized comes from the National Park Service's API: https://www.nps.gov/subjects/developer/api-documentation.htm </br>

Backend: Python/Flask
Database: PostgreSQL
ORM: SQLAlchemy
Frontend: Bootstrap