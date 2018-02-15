//////////////////////////////////////////////////////////////////////
///////// 1. Define Main Function ////////////////////////////////////
//////////////////////////////////////////////////////////////////////
////////// Author: Denis Torre
////////// Affiliation: Ma'ayan Laboratory, Icahn School of Medicine at Mount Sinai

function main() {

	addModal();
	addButtons();
	addEventListeners();

}

//////////////////////////////////////////////////////////////////////
///////// 2. Define Functions ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////
////////// 1. modal /////////////////////////
//////////////////////////////////////////////////

var modal = {

	Section: function(title, tool_string, display='block') {
		section = $('<div>', {'class': 'modal-section'}).html($('<span>').html(title)).css('display', display);
		if (tool_string) {
			section.append($('<input>', {'type': 'hidden', 'name': 'tool_string', 'value': tool_string}));
		}
		return section;
	},

	Text: function(text) {
		return $('<div>', {'class': 'modal-text'}).html(text);
	},

	Tool: function(tool) {
		return $('<div>', {'class': 'modal-tool-card'})
					.append($('<input>', {'type': 'checkbox', 'class': 'modal-tool-checkbox', 'id': tool['tool_string']+'-checkbox', 'value': tool['tool_string'], 'name': 'input-tools', 'required': 'true', 'checked': tool['default_selected'] > 0}).data(tool))
					.append($('<label>', {'class': 'modal-tool-label', 'for': tool['tool_string']+'-checkbox'})
						.append($('<div>', {'class': 'modal-tool-icon-wrapper'})
							.html($('<img>', {'class': 'modal-tool-icon', 'src': chrome.extension.getURL('icons/'+tool['tool_string']+'.png')})))
						.append($('<div>', {'class': 'modal-tool-text'})
							.append($('<div>', {'class': 'modal-tool-title'}).html(tool['tool_name']))
							.append($('<div>', {'class': 'modal-tool-description'}).html(tool['tool_description'])))
					);
	},

	Table: function(samples) {
		var table = $('<table>', {'class': 'group-table'})
						.append($('<tr>')
							.append($('<th>').html('Group A'))
							.append($('<th>').html('Sample Title'))
							.append($('<th>').html('Group B'))
						);

		$.each(samples, function(index, elem) {
			table.append($('<tr>')
				.append($('<td>').append($('<input>', {'class': 'group-table-radio', 'type': 'radio', 'id': elem['gsm']+'-A', 'name': elem['gsm'], 'value': 'A', 'checked': false})).append($('<label>', {'for': elem['gsm']+'-A'}).html($('<div>').html(elem['gsm']))))
				.append($('<td>').html(elem['sample_title']))
				.append($('<td>').append($('<input>', {'class': 'group-table-radio', 'type': 'radio', 'id': elem['gsm']+'-B', 'name': elem['gsm'], 'value': 'B', 'checked': false})).append($('<label>', {'for': elem['gsm']+'-B'}).html($('<div>').html(elem['gsm']))))
			)
		})
		return table;
	},

	Input: function(label, description='', name='', value='', type='text', options=[]) {
		var input;
		// Text input
		if (type === 'text') {
			input = $('<input>', {'type': 'text', 'class': 'modal-input-text', 'name': name, 'value': value});

		// Select input
		} else if (type === 'select') {
			input = $('<select>', {'class': 'modal-input-select', 'name': name});
			$.each(options, function(index, elem) {
				input.append($('<option>').html(elem).attr('selected', elem === value));
			})
		}

		// Return
		return $('<div>', {'class': 'modal-input-row'})
					.append($('<label>', {'class': 'modal-input-label'}).html(label))
					.append($('<div>', {'class': 'modal-input-tooltip'}).html(description))
					.append(input)
	}
}

//////////////////////////////////////////////////
////////// 1. addButtons /////////////////////////
//////////////////////////////////////////////////

function addButtons() {
	// Get Entries
	entries = {}
	$('.rprt').each(function(i, elem) {entries[$(elem).find('dt:contains("Accession:")').next().text()] = $(elem)});

	// Get Samples
	$.ajax({	
		url: "http://amp.pharm.mssm.edu/notebook-generator-server/api/samples",
		method: "POST",
		data: JSON.stringify({'gse': Object.keys(entries)}),
		dataType: 'json',
		success: function(res) {

			// Loop through GSE
			$.each(res, function(gse, samples) {

				// Check if GSE has been processed
				if (Object.keys(samples).length) {

					// Add Button
					entries[gse].append(
						$('<div>', {'class': 'notebook-generator-link'})
							.append($('<img>', {'src': chrome.extension.getURL('icons/icon.png')}))
							.append($('<span>').html('Launch Notebook'))
							.data('samples', samples)
							.data('gse', gse)
							.data('gpl', Object.keys(samples)[0])
					);
				}				
			})

			$('.notebook-generator-link').first().click();
			$('#next-step').click();
		}			
	})
}

//////////////////////////////////////////////////
////////// 2. Add Modal //////////////////////////
//////////////////////////////////////////////////

function addModal() {
	// Add Template
	$('body').append(
		$('<div>', {'id': 'notebook-generator-modal', 'class': 'modal'})
			.html($('<div>', {'id': 'modal-wrapper'})
					.append($('<div>', {'id': 'modal-head'})
						.append($('<div>', {'id': 'modal-title'}))
						.append($('<div>', {'id': 'close-modal'}))
					)
					.append($('<div>', {'id': 'modal-body'})
						.append($('<form>', {'id': 'tool-form', 'class': 'modal-form'})
							.html(modal.Text('To start building your notebook, select analysis tools by choosing from the options below:'))
						)
						.append($('<form>', {'id': 'group-form', 'class': 'modal-form'}))
						.append($('<form>', {'id': 'configuration-form', 'class': 'modal-form'}))
						.append($('<form>', {'id': 'results-form', 'class': 'modal-form'}))
					)
					.append($('<div>', {'id': 'modal-footer'})
						.append($('<button>', {'id': 'previous-step', 'class': 'modal-button'}).html('Back'))
						.append($('<button>', {'id': 'next-step', 'class': 'modal-button'}).html('Next'))
					)
			)
	)

	// Add Tools
	signature_tools = [];
	$.ajax({
		url: "http://amp.pharm.mssm.edu/notebook-generator-server/api/tools",
		method: "POST",
		dataType: 'json',
		success: function(res) {
			$.each(res['sections'], function(index, section) {
				// Add button
				$('#tool-form').append(modal.Section(section['section_name']));
				$.each(section['tool_string'], function(index, tool_string) {
					$('#tool-form').append(modal.Tool(res['tools'][tool_string]));
					// Add to list
					if (res['tools'][tool_string]['requires_signature']) {
						signature_tools.push(tool_string);
					}
				})
			})
		}
	})
}

//////////////////////////////////////////////////
////////// 3. Add Tools //////////////////////////
//////////////////////////////////////////////////

function addTools() {
	// Add Text
	$('#modal-title').html('Select Tools');
	$('#notebook-generator-modal').data('step', 'add-tools');
	$('#next-step').html('Next').removeClass('active');
	$('#previous-step').html('Cancel');

	// Toggle
	$('.modal-form').hide();
	$('#tool-form').show();
}

//////////////////////////////////////////////////
////////// 4. Get Tools //////////////////////////
//////////////////////////////////////////////////

function getTools() {
	var selected_tools = {'tools': [], 'requires_signature': false};
	$('.modal-tool-checkbox:checked').each(function(index, elem){
		var tool = $(elem).data();
		selected_tools['tools'].push(tool);
		if (tool['requires_signature']) {
			selected_tools['requires_signature'] = true;
		}
	});
	return selected_tools
}

//////////////////////////////////////////////////
////////// 5. Add Groups /////////////////////////
//////////////////////////////////////////////////

function addGroups() {

	// Add Text
	$('#modal-title').html('Set Groups');
	$('#notebook-generator-modal').data('step', 'add-groups');
	$('#next-step').html('Next').removeClass('active');
	$('#previous-step').html('Back');

	// Add Content
	$('#group-form').html('');
	$('#group-form').append(modal.Text('One or more of the selected tools requires a gene expression signature. To proceed, complete the information below:'));
	$('#group-form').append(modal.Section('Select Samples'));
	$('#group-form').append(modal.Text('First, set the conditions by adding at least three samples per group.'));
	var samples = Object.values($('#notebook-generator-modal').data('samples'))[0];
	$('#group-form').append(modal.Table(samples));
	$('#group-form').append(modal.Section('Optional Settings'));
	$('#group-form').append(modal.Text('Optionally, select the differential expression method and add a custom label for each group.'));
	$('#group-form').append(modal.Input('Method:', 'DE Method', 'method', 'limma', 'select', ['limma']));
	$('#group-form').append(modal.Input('Group A name:', 'Label to assign to Group A', 'group_a', 'Group A'));
	$('#group-form').append(modal.Input('Group B name:', 'Label to assign to Group B', 'group_b', 'Group B'));

	// Toggle
	$('.modal-form').hide();
	$('#group-form').show();
}

//////////////////////////////////////////////////
////////// 6. Get Groups /////////////////////////
//////////////////////////////////////////////////

function getGroups() {
	
	// Set Variables
	var groups = {'A': {'name': '', 'samples': []}, 'B': {'name': '', 'samples': []}},
		form=$('#group-form').serializeArray();

	// Add labels
	$.each(form, function(index, elem) {
		var name = elem['name'], value = elem['value'];

		// Group labels
		if (value) {
			if (['group_a', 'group_b'].indexOf(name) > -1 ) {
				var group = name.split('_')[1].toUpperCase();
				groups[group]['name'] = value;
			} else if (name === 'method') {
				groups['method'] = value;
			} else {
				// Sample labels
				groups[value]['samples'].push(name);
			}
		}
	})

	return groups
}

//////////////////////////////////////////////////
////////// 7. Add Configuration //////////////////
//////////////////////////////////////////////////

function addConfiguration(selected_tools, groups) {

	// Add Text
	$('#modal-title').html('Review');
	$('#notebook-generator-modal').data('step', 'add-configuration');
	$('#previous-step').html('Back');
	$('#next-step').html('Get Notebook').addClass('active');

	// Add Content
	$('#configuration-form').html('');
	$('#configuration-form').append(modal.Text('Optionally, review the notebook and modify optional parameters:'));
	$('#configuration-form').append(modal.Section('General Settings'));
	$('#configuration-form').append(modal.Input('Notebook Title:', 'Title of the Jupyter Notebook', 'title', $('#notebook-generator-modal').data('gse')+' Analysis Notebook'));
	$('#configuration-form').append(modal.Input('Live:', 'Indicates whether the Jupyter Notebook should be deployed in a live server or as a static HTML report', 'live', 'False', 'select', ['False', 'True']));

	// Add Tool Parameters
	$.each(selected_tools['tools'], function(index, tool) {
		// if (tool['parameters'].length > 0) {
		display = tool['parameters'].length > 0 ? 'block' : 'none'
		$('#configuration-form').append(modal.Section(tool['tool_name'], tool['tool_string'], display));
		$.each(tool['parameters'], function(parameter_id, parameter) {
			var value, options = [];
			$.each(parameter['values'], function(index, option) { options.push(option["value"]); if (option["default"]){value = option["value"]}; });
			$('#configuration-form').append(modal.Input(parameter["parameter_name"]+' :', parameter["parameter_description"], parameter["parameter_string"], value, 'select', options));
		})
		// }
	})

	// Toggle
	$('.modal-form').hide();
	$('#configuration-form').show();
}

//////////////////////////////////////////////////
////////// 8. Get Configuration //////////////////
//////////////////////////////////////////////////

function getConfiguration() {

	// Initialize
	var current_tool, configuration = {'notebook':{}, 'tools':[]};

	// Serialize form
	form = $('#configuration-form').serializeArray();

	// Loop through form
	$.each(form, function(index, parameter) {

		// Add general parameters
		if (['title', 'live'].indexOf(parameter['name']) > -1) {
			configuration['notebook'][parameter['name']] = parameter['value'];
		}

		// Get current tool
		if (parameter['name'] === 'tool_string') {
			current_tool = parameter['value'];
			configuration['tools'].push({'tool_string': current_tool, 'parameters': {}});
 		}

		// Add tool parameters
		if (current_tool && parameter['name'] != 'tool_string') {
			configuration['tools'][configuration['tools'].length-1]['parameters'][parameter['name']] = parameter['value'];
		}

	})

	// Add data
	configuration['data'] = {'source': 'archs4', 'parameters': {'gse': $('#notebook-generator-modal').data('gse'), 'platform': $('#notebook-generator-modal').data('gpl')}}
	configuration['notebook']['version'] = 'v0.2'

	// Return
	return configuration
}

//////////////////////////////////////////////////
////////// 9. Get Notebook Link //////////////////
//////////////////////////////////////////////////

function addNotebookLink(configuration) {
	$.ajax({	
		url: "http://amp.pharm.mssm.edu/notebook-generator-server/api/generate",
		method: "POST",
		data: JSON.stringify(configuration),
		contentType: "application/json; charset=utf-8",
		dataType: 'json',
		success: function(res) {
			$('.sk-circle').remove();
			$('#modal-loading-text').html('Your Notebook is available at the link below:')
			$('#results-form').append($('<div>', {'id': 'modal-notebook-results'}).html($('<a>', {'id': 'modal-notebook-link', 'href': res['notebook_url'], 'target': '_blank'}).html('Open Notebook')));
		}//,
		// error: function(e) {
		// 	$('.sk-circle').remove();
		// 	$('#modal-loading-text').html('Sorry, there has been an error.<br>&nbsp')
		// }
	})
}

//////////////////////////////////////////////////
////////// 10. Add Notebook //////////////////////
//////////////////////////////////////////////////

function showNotebookForm() {
	// Add Text
	$('#modal-title').html('Results');
	$('#next-step').html('Done').addClass('active');
	$('#notebook-generator-modal').data('step', 'results');

	// Add text
	$('#results-form').html('');
	$('#results-form').append($('<div>', {'id': 'modal-loading-text'}).html('Your Jupyter Notebook is being prepared.'))
	$('#results-form').append('<div class="sk-circle"><div class="sk-circle1 sk-child"></div><div class="sk-circle2 sk-child"></div><div class="sk-circle3 sk-child"></div><div class="sk-circle4 sk-child"></div><div class="sk-circle5 sk-child"></div><div class="sk-circle6 sk-child"></div><div class="sk-circle7 sk-child"></div><div class="sk-circle8 sk-child"></div><div class="sk-circle9 sk-child"></div><div class="sk-circle10 sk-child"></div><div class="sk-circle11 sk-child"></div><div class="sk-circle12 sk-child"></div></div>');

	// Toggle
	$('.modal-form').hide();
	$('#results-form').show();
}

//////////////////////////////////////////////////
////////// 11. Event Listeners ///////////////////
//////////////////////////////////////////////////

function addEventListeners() {

	// Variables
	var step, selected_tools, groups={}, configuration;

	// open modal
	$(document).on('click', '.notebook-generator-link', function(evt) {
		$('#notebook-generator-modal').css('display', 'block');
		$('#notebook-generator-modal').data('gse', $(evt.target).data('gse'));
		$('#notebook-generator-modal').data('gpl', $(evt.target).data('gpl'));
		$('#notebook-generator-modal').data('samples', $(evt.target).data('samples'));
		addTools();
		$("body").css("overflow-y", "hidden");
	})

	// close modal
	// $(document).click(function(evt) {
	// 	if ($(evt.target).attr('id') === 'notebook-generator-modal' ) {
	// 		$('#notebook-generator-modal').css('display', 'none');
	// 		$('#notebook-generator-modal form').css('display', 'none');
	// 	}
	// })

	// Next step
	$('#next-step').click(function(evt) {
		var step = $('#notebook-generator-modal').data('step');

		// Add Tools Step
		if (step === 'add-tools') {

			// Get Tools
			selected_tools = getTools();

			// If no tools selected
			if (selected_tools['tools'].length === 0) {
				alert('Please select one or more tools to continue.')
			} else {

				// If tools require signature
				if (selected_tools['requires_signature']) {
					addGroups();

				// If tools do not require signature
				} else {
					addConfiguration(selected_tools, groups);
				}
			}
		}

		// Add Groups Step
		else if (step === 'add-groups') {

			// Get Groups
			groups = getGroups();

			// Get Group Sizes
			small_groups = [];
			$.each(groups, function(key, value) { if (key != 'method' && value['samples'].length < 3) { small_groups.push(key) } })

			// Alert if not enough samples selected
			if (small_groups.length > 0) {
				alert('To proceed, please add at least three samples to group(s) '+small_groups.join(' and ')+'.')

			// Otherwise continue
			} else {
				addConfiguration(selected_tools, groups)
			}
		}

		// Add Configuration Step
		else if (step === 'add-configuration') {

			// Get Configuration
			configuration = getConfiguration();

			// Add groups
			configuration['signature'] = groups;
			
			// Convert to array
			console.log(JSON.stringify(configuration));

			// Get Notebook
			showNotebookForm();
			addNotebookLink(configuration);

		}

		// Results
		else if (step === 'results') {
			// Close modal
			$('#notebook-generator-modal').css('display', 'none');
			$('#notebook-generator-modal form').css('display', 'none');
			$("body").css("overflow-y", "");
		}

		// De-focus Button
		$(evt.target).blur();
	})

	// Previous Step
	$('#previous-step').click(function(evt) {

		// Get Step
		var step = $('#notebook-generator-modal').data('step');

		// Toggle Forms
		$('.modal-form').hide();

		// Add Tools
		if (step === 'add-tools') {
			// $('#notebook-generator-modal').click();
			$('#notebook-generator-modal').css('display', 'none');
			$('#notebook-generator-modal form').css('display', 'none');
			$("body").css("overflow-y", "");
		} else if (step === 'add-groups') {
			$('#tool-form').show();
			$('#notebook-generator-modal').data('step', 'add-tools');
			$('#previous-step').html('Cancel').removeClass('active');
			$('#modal-title').html('Select Tools');
		} else if (step === 'add-configuration') {
			// If Groups are required
			if (selected_tools['requires_signature']) {
				$('#modal-title').html('Set Groups');
				$('#group-form').show();
				$('#notebook-generator-modal').data('step', 'add-groups');
				$('#previous-step').html('Back').removeClass('active');
				$('#next-step').html('Next');
			// If groups aren't required
			} else {
				$('#tool-form').show();
				$('#modal-title').html('Select Tools');
				$('#notebook-generator-modal').data('step', 'add-tools');
				$('#previous-step').html('Cancel');
				$('#next-step').html('Next');
			}
		} else if (step === 'results') {
			$('#modal-title').html('Review');
			$('#results-form').hide();
			$('#configuration-form').show();
			$('#notebook-generator-modal').data('step', 'add-configuration');
			$('#next-step').html('Generate Notebook').addClass('active');
		}

		// De-focus Button
		$(evt.target).blur();
	})

	// Radio
	$(document).on('click', 'label', function(evt){
		var radio = $(evt.target).parents('td').find('input[type="radio"]');
		if (radio.length > 0) {
			evt.preventDefault();
			radio.prop('checked', !radio.prop('checked'))
		}
	})

	// Esc
	$(document).keyup(function(e) {
	     if (e.keyCode == 27) {
	        $('#notebook-generator-modal').click();
	    }
	});
}


//////////////////////////////////////////////////////////////////////
///////// 3. Run Main Function ///////////////////////////////////////
//////////////////////////////////////////////////////////////////////
main();
