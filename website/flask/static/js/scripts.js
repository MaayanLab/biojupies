/********************************/
/********** Scripts *************/
/********************************/

function goBack() {
    window.history.back();
}

$('.info-toggle').click(function(evt) {
	evt.preventDefault();
	var $button = $(evt.target),
		$icon = $button.parents('label').find('i'),
		id = $button.parents('label').attr('for');
	$('#'+id+'-info').collapse('toggle');
	$icon.toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
})