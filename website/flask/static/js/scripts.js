/********************************/
/********** Scripts *************/
/********************************/

function goBack() {
    window.history.back();
}

// Tooltip and Popover
$('[data-toggle="tooltip"]').tooltip(); 
$('[data-toggle="popover"]').popover(); 

// Card Collapse Info
$('.info-toggle').click(function(evt) {
	evt.preventDefault();
	var $button = $(evt.target),
		$icon = $button.parents('label').find('i'),
		id = $button.parents('label').attr('for');
	$('#'+id+'-info').collapse('toggle');
	$icon.toggleClass('fa-chevron-down').toggleClass('fa-chevron-up');
})

// Preview Table
function addPreviewTable(response, metadata=true) {

	// Define table
	var $table = $('<table>', {'class': 'table-striped w-100'}).append($('<thead>').append($('<tr>', {'class': 'very-small text-center border-grey border-left-0 border-right-0'}))).append($('<tbody>'));

	// Add headers
	label = metadata ? 'Gene' : 'Sample'
	$table.find('tr').append($('<th>', {'class': 'px-2 py-1'}).html(label));
	$.each(response['columns'], function(i, col) {
		$table.find('tr').append($('<th>', {'class': 'px-2 py-1'}).html(col));
	})

	// Get row number
	n = metadata ? 6 : response['index'].length

	// Add rows
	for (i=0; i<n; i++) {
		var $tr = $('<tr>').append($('<td>', {'class': 'bold text-center px-2 py-1'}).html(response['index'][i]));
		$.each(response['data'][i], function(i, val) {
			$tr.append($('<td>', {'class': 'light text-center tiny'}).html(val));
		})
		$table.find('tbody').append($tr);
	}

	// Add
	$('#preview').html($table);
}

// Serialize table
function serializeTable($table) {
	// Initialize results
	var data = [];

	// Loop through rows
	$table.find('tr').each(function(i, tr) {

		// Get cells
		var cells = i === 0 ? $(tr).find('th') : $(tr).find('td');

		// Get values
		var values = [];
		$.each(cells, function(i, cell) {
			var value = $(cell).find('input').length ? $(cell).find('input').val() : $(cell).html();
			values.push(value);
		})

		// Append values
		data.push(values);
	})

	// Return data
	return data
}

// Array difference
Array.prototype.diff = function (a) {
    return this.filter(function (i) {
        return a.indexOf(i) === -1;
    });
};
