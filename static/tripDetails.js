$possTabs = $("#possibility-tabs")
$stayTab = $("#stay-tab");
$stayTable = $("#stay-table");
$visitTab = $("#visit-tab");
$visitTable = $("#visit-table")
$doTab = $("#do-tab")
$doTable = $("#do-table")
$possTable = $("#poss-table")
$addModal = $('#add-modal')
allTables = [$stayTable, $visitTable, $doTable]
allTabs = [$stayTab, $visitTab, $doTab]

$stayTable.on("click", function(e){
	e.preventDefault();
	renderModal(e);
})

$visitTable.on("click", async function(e){
	e.preventDefault();
	await renderVisitModal(e)
})

$('#close-btn').on('click', hanldeClose)
function hanldeClose(e){
	$addModal.addClass("d-none");
	$('#activities-select').empty();
	$('#modal-title').empty();
}

function renderModal(e){
	let title = $(e.target).text();
	$('#modal-title').append(
		`<h3 class="mt-2">Stay At ${title}</h3>`
	);
	$('#stay-assign-form').append(`
		<input type='hidden' name='poi-name' value='${title}'>
	`)
	$("#stay-assign-form").removeClass("d-none")
	$("#visit-assign-form").addClass("d-none")
	$addModal.removeClass("d-none")
}

async function renderVisitModal(e){
	let title = $(e.target).text();
	let poiId = $(e.target).prop("id")
	let resp = await axios.get(`/api/poi/${poiId}/activities`)
	let activities = resp.data
	console.log(activities)
	$('#modal-title').append(
		`<h3 class="mt-2">Visit ${title}</h3>`
	);
	for(let act of activities){
		$("#activities-select").append(
			`<div class="form-check">
				<input class="form-check-input" type="checkbox" value="" name="${act.id}" id="${act.id}"/>
				<label class="form-check-label" for="${act.name}">
					${act.name}
					</label>
			</div>`
		)
	}
	$("#visit-assign-form").append(
		`<input type=hidden name="poi-id" value="${poiId}">`
	)

	$("#stay-assign-form").addClass("d-none")
	$("#visit-assign-form").removeClass("d-none")
	$addModal.removeClass("d-none")
}

$possTabs.on("click", function(e){
	e.preventDefault();
	const $table = determineTable(e);
	const $tab = $(e.target);

	const index = allTables.indexOf($table);

	const hideTables = [...allTables];
	hideTables.splice(index,1);
	hideTables.forEach(($t) => $t.addClass("d-none"));

	const inactiveTabs = [...allTabs];
	inactiveTabs.splice(index,1);
	inactiveTabs.forEach(($t)=> $t.removeClass('active'));

	$tab.addClass("active");
	$table.removeClass("d-none");
})

function determineTable(e){
	e.preventDefault();
	if($(e.target).is($stayTab)){
		return $stayTable
	};
	if($(e.target).is($visitTab)){
		return $visitTable
	};
	if($(e.target).is($doTab)){
		return $doTable
	}
}


$('#editModal').on('show.bs.modal', async function(evt){
	const tripId = parseInt($(evt.relatedTarget).data('bs-tripid'))
	const dayId =  $(evt.relatedTarget).data('bs-dayid');
	const editType = $(evt.relatedTarget).data('bs-type');
	console.log(editType)
	const resp = await axios.get(`/api/trips/${tripId}/options`)
	const tripOptions = resp.data
	console.log(tripOptions)

	$(".modal-body").empty()

	if(editType === "campground"){

		$("#editModalLabel").html("Update Campground")
		$(".modal-body").append(
			`<form action="/trips/${tripId}/campground/update" method="POST">
			<div class="mb-3">
				<label class="form-label" for="select-campground">
					Select A Different Campground
				</label>
				<select class="form-select" id="select-campground" name="select-campground">
				</select>
				<input type="hidden" name="dayId" value="${dayId}"
			</div>
			<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
				Close
			</button>
		  	<button type="submit" class="btn btn-primary">
				Update
			</button>
			</form>`
		)
		for(let c of tripOptions.campgrounds){
			$("#select-campground").append(
				`<option value="${c.id}">${c.name}</option>`
			)
		}
	}

	if(editType === "park"){
		$("#editModalLabel").html("Add a Park")
		$(".modal-body").append(
			`<form action="/trips/${tripId}/poi/assign" method="POST">
			<div class="mb-3">
				<label class="form-label" for="poi-id">
					Select A Park
				</label>
				<select class="form-select" id="park" name="poi-id">
				</select>
				<input type="hidden" name="day-id" value="${dayId}"
			</div>
			<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
				Close
			</button>
		  	<button type="submit" id="update-btn" class="btn btn-primary">
				Update
			</button>
			</form`
		)
		for(let p of tripOptions.parks){
			$("#park").append(
				`<option value="${p.id}">${p.name}</option>`
			)
		}
	}
})
	

// $("#update-button").on('click', ()=> $(".modal-body").empty())


