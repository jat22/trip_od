const $addModal = $('#addModal')
const $modalBody = $('.modal-body')
const $tripSelect = $("#trip-select")

$addModal.on('show.bs.modal', async function(evt){
	const resp = await axios.get(`/api/user/trips`)
	const trips = resp.data

	if(trips.length === 0){
		$modalBody.append(
			`<h6>It doesn't look like you have any trips save.</h6>
			<a href="/trips/create" class="btn btn-outline-success mb-2">
				Create A New Trip
			</a>`
		)
		return
	}

	$modalBody.append(
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
		$tripSelect.append(
			`<option value="${trip.id}">${trip.name}</option>`
		)
	}
})