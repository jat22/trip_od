const $addToTripBtn = $("#add-to-trip-btn")

$('#addModal').on('show.bs.modal', async function(evt){
	const resp = await axios.get(`/api/user/trips`)
	const trips = resp.data

	if(trips.length === 0){
		$(".modal-body").append(
			`<h6>It doesn't look like you have any trips save.</h6>
			<a href="/trips/create" class="btn btn-outline-success mb-2">
				Create A New Trip
			</a>`
		)
		return
	}

	$(".modal-body").append(
		`<form action="/trips/poi/add" method="POST">
			<div class="mb-3">
				<label for="trip">Select Trip:</label>
				<select class="form-select" name="trip" id="trip-select"></select>
			</div>
			<button type="submit" id="submit-btn" class="btn btn-secondary btn-sm">Submit</button>
			<a href="" class="btn btn-outlin btn-sm">Cancel</a>
		</form>`
	);

	for(let trip of trips){
		$("#trip-select").append(
			`<option value="${trip.id}">${trip.name}</option>`
		)
	}
})

// async function showModal(e){
// 	e.preventDefault();
// 	const resp = await axios.get(`/api/user/trips`)
// 	const trips = resp.data

// 	if(trips.length === 0){
// 		$("#modal").removeClass("d-none")
// 		return
// 	}

// 	$(".modal-body").append(
// 		`<form action="/trips/poi/add" method="POST">
// 			<div class="mb-3">
// 				<label for="trip">Select Trip:</label>
// 				<select class="form-select" name="trip" id="trip-select"></select>
// 			</div>
// 			<button type="submit" id="submit-btn" class="btn btn-secondary btn-sm">Submit</button>
// 			<a href="" class="btn btn-outlin btn-sm">Cancel</a>
// 		</form>`
// 	)
// 	for(let trip of trips){
// 		$("#trip-select").append(
// 			`<option value="${trip.id}">${trip.name}</option>`
// 		)
// 	}
// }

// $("#submit-btn").on("click", handleAdd)

// async function handleAdd(e){
// 	e.preventDefault();
// 	$("#modal").addClass("d-none");
// 	let tripId = $("#trip-select").val()
// 	let poiId = $("#poi-id").val()
// 	console.log(tripId, poiId)
// 	let resp = await axios.post(`/api/trips/${tripId}/poi/${poiId}`)

// }