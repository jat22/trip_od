const $searchButton = $("#search-btn");
const $term = $("#term");
const $cityStateSearch = $("#city-state-search");
const $poiSearch = $("#poi-search");
const $city = $("#city");
const $state = $("#state");
const $locationRadioBtns = $("#location-radio-btns")
const $poiRadio = $("#poi-radio")
const $poi = $("#poi")
const $cityStateRadio = $("#city-state-radio");
const $popUpForm = $(".pop-up-form");
const $cityOptionList = $("#city-options");

$locationRadioBtns.on("click", handleRadio)
$searchButton.on("click", handleSearch)
$cityOptionList.on("click", handleSelectCity)

function doSearch(data){
	const searchData = JSON.stringify(data);
	window.location.href = `/search?data=${encodeURIComponent(searchData)}`
}

function handleRadio(e){
	if($cityStateRadio.is(" :checked")){
		$cityStateSearch.removeClass('d-none');
		$poiSearch.addClass('d-none');
	}
	if($poiRadio.is(" :checked")){
		console.log("poi checked")
		$poiSearch.removeClass('d-none');
		$cityStateSearch.addClass('d-none');

	}
}

async function handleSearch(e){
	e.preventDefault();
	
	if($cityStateRadio.is(":checked")){
		const resp = await axios.get("/api/geolocation", {params :
			{
				city : $city.val(),
				state : $state.val()
			}
		});

		const exactMatch = resp.data.filter((city)=>(
					city.city.toLowerCase() === $city.val().toLowerCase() 
					&& 
					city.state.toLowerCase() === $state.val().toLowerCase())
				)
		
		
		if(exactMatch.length === 1){
			console.log(exactMatch)
			const searchData = {
				term : $term.val(),
				lat : exactMatch[0].cords.lat,
				lon : exactMatch[0].cords.lon
			};
			doSearch(searchData);
		} else{
			resp.data.forEach((city) => {
				$cityOptions.append(
					`<li class="list-group-item list-group-item-action" data-lon="${city.cords.lon}" data-lat="${city.cords.lat}">
						${city.city}, ${city.state}
					</li>`
				)
			})
			$popUpForm.removeClass("d-none")
		}
	} else{
		const searchData = 
			{
				term : $term.val(),
				poi : $poi.val()
			}

		doSearch(searchData);
	}
}

function handleSelectCity(e){
	const searchData = 
		{
			term : $term,
			lon : $(e.target).data('lon'),
			lat : $(e.target).data('lat')
		};

	doSearch(searchData)
}