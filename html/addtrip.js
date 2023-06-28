const $popUpForm = $(".pop-up-form")
const $addBtn = $("#add-to-trip-btn")

function toggleForm(event) {
	event.preventDefault();
	$popUpForm.toggleClass("d-none")
}

$addBtn.on("click", toggleForm)