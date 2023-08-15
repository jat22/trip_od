$tripCards = $(".trip-card")

$tripCards.on("click", (e)=>{
	let tripId = $(e.target).closest($tripCards).prop('id');
	console.log(tripId)
	window.location.href = `/trips/${tripId}`
})