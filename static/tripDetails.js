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
$('#close-btn').on('click', hanldeClose)
function hanldeClose(e){
	$addModal.addClass("d-none");
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