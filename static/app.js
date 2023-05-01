const $searchParams = $('#search-params');

const $cityStateSelector = $('#city-state');
const $latLongSelector = $('#lat-long');

const $cityField = $("#city-field");
const $stateField = $("#state-field");
const $latField = $("#lat-field");
const $longField = $("#long-field");
const $radiusField = $("#radius-field")

const $searchButton = $("#search-btn");


const currSearch = "currSearch"

function toggleSearchType(){
	if($cityStateSelector.is(' :checked')){
		$cityField.show();
		$stateField.show();
		$latField.hide().val("");
		$longField.hide().val("");
	}
	if($latLongSelector.is(' :checked')){
		$cityField.hide().val("");
		$stateField.hide().val("");
		$latField.show();
		$longField.show();
	}
}

$searchParams.on('click', toggleSearchType);

async function executeSearch(event){
	event.preventDefault();
	response = await axios.get("/api/search", {params:
		{
			city : $cityField.val(),
			state : $stateField.val(),
			latitude : $latField.val(),
			longitude : $longField.val(),
			radius : $radiusField.val()
		}
	})

	localStorage.setItem(currSearch, JSON.stringify(response.data))

	window.location.href = "/trips/stay"
}

$searchButton.on("click", executeSearch);


$(document).ready(function(){
	if(window.location.href.indexOf("http://127.0.0.1:5000/trips/stay") > -1){
		campgrounds = JSON.parse(localStorage.getItem(currSearch)).campgrounds
		campgrounds.forEach(campground =>
			$("#results-list").append(
				`<li class="list-group-item">
					<a href="/campgrounds/${campground.id}">${campground.name}</a>
					<form action="/trips/campgrounds/${campground.id}/add" method="POST">
						<button type="submit" class="btn btn-sm btn-info">Add To Trip</button>
					</form>
				</li>`
			)
		)
	}
	if(window.location.href.indexOf("http://127.0.0.1:5000/trips/where") > -1){
		states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado", "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]

		states.forEach( state =>
			$("#state-field").append(`<option>${state}</option`)
		)
	}
})