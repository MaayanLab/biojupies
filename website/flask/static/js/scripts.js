/********************************/
/********** Scripts *************/
/********************************/

function goBack() {
    window.history.back();
}

$('.group_label').change(function(evt) {
	$('.'+$(evt.target).attr('name')).html($(evt.target).val());
})