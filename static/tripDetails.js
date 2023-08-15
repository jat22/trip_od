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