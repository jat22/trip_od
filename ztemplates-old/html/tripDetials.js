$possTabs = $("#possibility-tabs")
$stayTab = $("#stay-tab");
$stayTable = $("#stay-table");
$visitTab = $("#visit-tab");
$visitTable = $("#visit-table")
$doTab = $("#do-tab")
$doTable = $("#do-table")
allTables = [$stayTable, $visitTable, $doTable]
allTabs = [$stayTab, $visitTab, $doTab]

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