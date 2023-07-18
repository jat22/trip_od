const $typeMenu = $("#fac-type-menu")
const $searchResults = $("#results-tbody")



function handleSelect(e) {
	e.preventDefault();
	$searchResults.addClass("d-none");
	$searchResults.empty();
	const filterType = $(e.target).text();
	for(r of results){
		if(r.type === filterType || filterType === "All"){
			$searchResults.append(
				`<tr onclick="window.location='/poi/${r.id}';" >
					<td class="img-col align-middle">
						<img class="result-img" src="https://cdn.pixabay.com/photo/2020/06/14/17/57/mountains-5298769_1280.jpg">
					</td>
					<td class="name-col align-middle">${r.name}</td>
					<td class="loc-col align-middle">${r.city}, ${r.state}</td> 
				</tr>`
			)
		}
	}

	$searchResults.removeClass("d-none")
}
$typeMenu.on("click", handleSelect)