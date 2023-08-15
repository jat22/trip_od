const $addToTripBtn = $("#add-to-trip-btn")

$addToTripBtn.on("click", showModal);

async function showModal(e){
	e.preventDefault();
	const resp = await axios.get(`/api/user/trips`)
	const trips = resp.data

	if(trips.length === 0){
		$("#modal").removeClass("d-none")
		return
	}

	$("#trip-card").append(
		`<form action="/trips/poi/add" method="POST">
			<div class="mb-3">
				<label for="trip">Select Trip:</label>
				<select class="form-select" name="trip" id="trip-select"></select>
			</div>
			<button type="submit" id="submit-btn" class="btn btn-secondary btn-sm">Submit</button>
			<a href="" class="btn btn-outlin btn-sm">Cancel</a>
		</form>`
	)
	for(let trip of trips){
		$("#trip-select").append(
			`<option value="${trip.id}">${trip.name}</option>`
		)
	}
	$("#modal").removeClass("d-none")
}

$("#cancel-btn").on("click", hideModal);

function hideModal(e){
	e.preventDefault();
	$("#modal").addClass("d-none");
	// $("#trip-select").empty();
}

// $("#submit-btn").on("click", handleAdd)

// async function handleAdd(e){
// 	e.preventDefault();
// 	$("#modal").addClass("d-none");
// 	let tripId = $("#trip-select").val()
// 	let poiId = $("#poi-id").val()
// 	console.log(tripId, poiId)
// 	let resp = await axios.post(`/api/trips/${tripId}/poi/${poiId}`)

// }