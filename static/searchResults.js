const $campTab = $("#camp-tab")
const $parkTab = $("#park-tab")
const $parksTable = $("#parks-table")
const $campgroundsTable = $("#campgrounds-table")
const $parksBody = $("#parks-tbody")
const $campgroundBody = $("#campgrounds-tbody")

$("#type-tabs").on("click", function(evt){
	evt.preventDefault();
	$campTab.removeClass("active");
	$parkTab.removeClass("active")
	if($(evt.target).prop("id") == $campTab.prop("id")){
		$parksTable.addClass("d-none")
		$campgroundsTable.removeClass("d-none")
	} else if($(evt.target).prop("id") == $parkTab.prop('id')) {
		$($campgroundsTable.addClass('d-none'))
		$($parksTable.removeClass('d-none'))
	}
	$(evt.target).addClass("active")
})

$(document).ready(()=>{
	if($parksBody.children().length === 0){
		$parksBody.append(`<h2>No Parks Found</h2>`)
	}
	if($campgroundBody.children().length === 0){
		$campgroundBody.append(`<h2>No Campgrounds Found</h2>`)
	}
})




// const $typeMenu = $("#fac-type-menu")
// const $searchResults = $("#results-tbody")
// const $sortButton = $("#sort-button")


// const $typeTabs = $("#type-tabs")
// function handleSelect(e) {
// 	e.preventDefault();
// 	$searchResults.addClass("d-none");
// 	$searchResults.empty();
// 	const filterType = $(e.target).text();
// 	for(r of results){
// 		if(r.type === filterType || filterType === "All"){
// 			$searchResults.append(
// 				`<tr onclick="window.location='/poi/${r.id}';" >
// 					<td class="img-col align-middle">
// 						<img class="result-img" src="https://cdn.pixabay.com/photo/2020/06/14/17/57/mountains-5298769_1280.jpg">
// 					</td>
// 					<td class="name-col align-middle">${r.name}</td>
// 					<td class="loc-col align-middle">${r.city}, ${r.state}</td> 
// 				</tr>`
// 			)
// 		}
// 	}
// 	$sortButton.text(filterType)
// 	$searchResults.removeClass("d-none")
// }
// $typeMenu.on("click", handleSelect)