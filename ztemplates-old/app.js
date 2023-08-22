const $searchParams = $('#search-params');

const $cityStateSelector = $('#city-state');
const $latLongSelector = $('#lat-long');

const $cityField = $("#city-field");
const $stateField = $("#state-field");
const $cityStateRow = $("#city-state-row");
const $latField = $("#lat-field");
const $longField = $("#long-field");
const $latLongRow = $("#lat-long-row");
const $radiusField = $("#radius-field");

const $searchButton = $("#search-btn");


const currTrip = "currTrip"
const campOptions = "campOptions"
const actOptions = "actOptions"

function toggleSearchType(){
	if($cityStateSelector.is(' :checked')){
		$cityStateRow.show();
		$latLongRow.hide();
		$latField.val("");
		$longField.val("");
	}
	if($latLongSelector.is(' :checked')){
		$cityStateRow.hide();
		$cityField.val("");
		$stateField.val("");
		$latLongRow.show();
	}
}

$searchParams.on('click', toggleSearchType);
$(document).ready(toggleSearchType())

async function executeSearch(event){
	event.preventDefault();
	response = await axios.get("/api/search", {params:
		{
			city : $cityField.val(),
			state : $stateField.val(),
			latitude : $latField.val(),
			longitude : $longField.val(),
			radius : $radiusField.val(),
			tripId : tripId
		}
	})

	localStorage.setItem(currTrip, tripId)
	localStorage.setItem(campOptions, JSON.stringify(response.data.campgrounds))
	localStorage.setItem(actOptions, JSON.stringify(response.data.activities))

	window.location.href = `/trips/${tripId}/campgrounds`
}

$searchButton.on("click", executeSearch);

async function updateOptions(event){
	event.preventDefault();
	if (localStorage.getItem(currTrip) != tripId){
		response = await axios.get("/api/trip/options", {params: {trip_id : tripId}})

		localStorage.setItem(currTrip, tripId)
		localStorage.setItem(campOptions, JSON.stringify(response.data.campgrounds))
		localStorage.setItem(actOptions, JSON.stringify(response.data.activities))
	}

	if($(event.target).is("#more-acts-btn")){
		window.location.href = `/trips/${tripId}/activities`
	}

	if($(event.target).is("#more-camps-btn")){
		window.location.href = `/trips/${tripId}/campgrounds`
	}
}

$(".more-button").on("click", updateOptions)



$(document).ready(function(){

	if(window.location.href.indexOf(`http://127.0.0.1:5000/trips/${tripId}/where`) > -1){
		states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado", "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

		states.forEach( state =>
			$("#state-field").append(`<option>${state}</option`)
		)
	}

	if(window.location.href.indexOf(`http://127.0.0.1:5000/trips/${tripId}/campgrounds`) > -1){
		if(tripId != localStorage.getItem(currTrip)){
			updateOptions(tripId)
		}	
	
		const campgrounds = JSON.parse(localStorage.getItem(campOptions))

		console.log(campgrounds)
		campgrounds.forEach(campground =>
			$(".results-list").append(
				`<li class="list-group-item result-item bg-secondary bg-opacity-50">
					<div class="row">
						<div class="col-8">
							<a class="text-dark" href="/locations/${campground.id}/campground">
								${campground.name}
							</a>
						</div>
						<div class="col-4 d-flex justify-content-end">
							<form action="/trips/${tripId}/campgrounds/${campground.id}/add" method="POST">
								<button type="submit" class="btn btn-sm btn-info">
									Add To Trip
								</button>
							</form>
						</div>
					</div>
				</li>`
			)
		)
	}

	if(window.location.href.indexOf(`http://127.0.0.1:5000/trips/${tripId}/activities`) > -1){
		if(tripId != localStorage.getItem(currTrip)){
			updateOptions(tripId)
		}
	
		const activities = JSON.parse(localStorage.getItem(actOptions))

		console.log(activities)

		activities.forEach(function(activity){
			$(".results-list").append(
				`<li class="list-group-item result-item bg-secondary bg-opacity-50">
					<div class="row">
						<div class="col-8">
							<a class="link-dark " href="/trips/${tripId}/activity/${activity.id}">
								${activity.name}
							</a>
						</div>
					</div>
				</li>`
			);

		})
	}
	if(window.location.href.indexOf(`http://127.0.0.1:5000/trips/${tripId}/activity/${activityId}`) > -1){

		const activities = JSON.parse(localStorage.getItem(actOptions));

		const locations = activities.find(activity => activity.id == activityId).locations;

		console.log(locations)
		locations.forEach(function(location){
			$(".results-list").append(
				`<li class="list-group-item result-item bg-secondary bg-opacity-50">
					<div class="row">
						<div class="col-8">
							<a class="link-color" href="/locations/${location.id}/activity/${activityId}">
								${location.name}
							</a>
						</div>
						<div class="col-4 d-flex justify-content-end">
							<form action="/trips/${tripId}/act${activityId}/${location.id}/add" method="POST">
								<button class="btn btn-sm btn-info" type="submit">
									Add to Trip
								</button>
							</form>
						</div>
					</div>
				</li>`
			)})
	}

	
})