//////////////////////////////////////////////////////////////////////
///////// 1. Define Main Function ////////////////////////////////////
//////////////////////////////////////////////////////////////////////
////////// Author: Denis Torre
////////// Affiliation: Ma'ayan Laboratory, Icahn School of Medicine at Mount Sinai

function main() {

	addButtons();
	addModal();
	addEventListeners();

	// $('#notebook-generator-modal').css('display', 'block');
	// addTools();
	// $('#pca-checkbox').attr('checked', 'true');
	// $('#tsne-checkbox').attr('checked', 'true');
	// $('#clustered_heatmap-checkbox').attr('checked', 'true');
	// $('#next-step').click();
	// $('#next-step').click();

}

//////////////////////////////////////////////////////////////////////
///////// 2. Define Functions ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////

sections = {
	"Dimensionality Reduction": ["pca", "tsne"],
	"Data Visualization": ["clustered_heatmap", "library_size_analysis"],
	"Differential Expression": ["de_table", "volcano_plot", "ma_plot"],
	"Signature Analysis": ["enrichr", "l1000cds2"]
};

tools = {
	"pca": {
		"tool_name": "PCA",
		"tool_string": "pca",
		"tool_description": "Linear dimensionality reduction technique",
		"requires_signature": false,
		"parameters": [
			{
				"parameter_name": "Dimensions",
				"parameter_string": "dimensions",
				"parameter_description": "The number of dimensions to reduce the dataset to",
				"values": [{"value": 2, "default": 0}, {"value": 3, "default": 0}]
			},
			{
				"parameter_name": "Number of genes",
				"parameter_string": "nr_genes",
				"parameter_description": "Top number of genes to take",
				"values": [{"value": 500, "default": 0}, {"value": 1000, "default": 1}, {"value": 5000, "default": 0}]
			},
			{
				"parameter_name": "Normalization Method",
				"parameter_string": "normalization",
				"parameter_description": "Method to be used to normalize the data",
				"values": [{"value": "Z-score", "default": 1}, {"value": "voom", "default": 0}, {"value": "vst", "default": 0}, {"value": "Size Factors", "default": 0}, {"value": "None", "default": 0}]
			}
		]
	},
	"tsne": {
		"tool_name": "t-SNE",
		"tool_string": "tsne",
		"tool_description": "Nonlinear dimensionality reduction technique",
		"requires_signature": false,
		"parameters": [
			{
				"parameter_name": "Dimensions",
				"parameter_string": "dimensions",
				"parameter_description": "The number of dimensions to reduce the dataset to",
				"values": [{"value": 2, "default": 0}, {"value": 3, "default": 0}]
			},
			{
				"parameter_name": "Number of genes",
				"parameter_string": "nr_genes",
				"parameter_description": "Top number of genes to take",
				"values": [{"value": 500, "default": 0}, {"value": 1000, "default": 1}, {"value": 5000, "default": 0}]
			},
			{
				"parameter_name": "Normalization Method",
				"parameter_string": "normalization",
				"parameter_description": "Method to be used to normalize the data",
				"values": [{"value": "Z-score", "default": 1}, {"value": "voom", "default": 0}, {"value": "vst", "default": 0}, {"value": "Size Factors", "default": 0}, {"value": "None", "default": 0}]
			}
		]
	},
	"clustered_heatmap": {
		"tool_name": "Clustered Heatmap",
		"tool_string": "clustered_heatmap",
		"tool_description": "Clustered heatmap analysis",
		"requires_signature": false,
		"parameters": [
			{
				"parameter_name": "Number of genes",
				"parameter_string": "nr_genes",
				"parameter_description": "Top number of genes to take",
				"values": [{"value": 500, "default": 0}, {"value": 1000, "default": 1}, {"value": 5000, "default": 0}]
			},
			{
				"parameter_name": "Normalization Method",
				"parameter_string": "normalization",
				"parameter_description": "Method to be used to normalize the data",
				"values": [{"value": "Z-score", "default": 1}, {"value": "voom", "default": 0}, {"value": "vst", "default": 0}, {"value": "Size Factors", "default": 0}, {"value": "None", "default": 0}]
			}
		]
	},
	"library_size_analysis": {
		"tool_name": "Library Size Analysis",
		"tool_string": "library_size_analysis",
		"tool_description": "Analysis of readcount distribution for the samples within the dataset",
		"requires_signature": false,
		"parameters": [
		]
	},
	"de_table": {
		"tool_name": "Differential Expression Analysis",
		"tool_string": "de_table",
		"tool_description": "Differential expression analysis table",
		"requires_signature": true,
		"parameters": [
			 {
				"parameter_name": "Method",
				"parameter_string": "method",
				"parameter_description": "DE Method",
				"values": [{"value": "limma", "default": 1}, {"value": "deseq", "default": 0}, {"value": "CD", "default": 0}]
			}
		]
	},
	"volcano_plot": {
		"tool_name": "Volcano Plot",
		"tool_string": "volcano_plot",
		"tool_description": "Plot the logFC and logP values resulting from a differential expression analysis",
		"requires_signature": true,
		"parameters": [
			 {
				"parameter_name": "Method",
				"parameter_string": "method",
				"parameter_description": "DE Method",
				"values": [{"value": "limma", "default": 1}, {"value": "deseq", "default": 0}, {"value": "CD", "default": 0}]
			}
		]
	},
	"ma_plot": {
		"tool_name": "MA Plot",
		"tool_string": "ma_plot",
		"tool_description": "Plot the logFC and average expression values resulting from a differential expression analysis",
		"requires_signature": true,
		"parameters": [
			 {
				"parameter_name": "Method",
				"parameter_string": "method",
				"parameter_description": "DE Method",
				"values": [{"value": "limma", "default": 1}, {"value": "deseq", "default": 0}, {"value": "CD", "default": 0}]
			}
		]
	},
	"enrichr": {
		"tool_name": "Enrichr",
		"tool_string": "enrichr",
		"tool_description": "Enrichment analysis of the top most overexpressed and underexpressed genes from a differential expression analysis.",
		"requires_signature": true,
		"parameters": [
			 {
				"parameter_name": "Method",
				"parameter_string": "method",
				"parameter_description": "DE Method",
				"values": [{"value": "limma", "default": 1}, {"value": "deseq", "default": 0}, {"value": "CD", "default": 0}]
			}
		]
	},
	"l1000cds2": {
		"tool_name": "L1000CDS2",
		"tool_string": "l1000cds2",
		"tool_description": "Identify small molecules which mimic or reverse a given differential gene expression signature.",
		"requires_signature": true,
		"parameters": [
			 {
				"parameter_name": "Direction",
				"parameter_string": "direction",
				"parameter_description": "DE Method",
				"values": [{"value": "both", "default": 1}, {"value": "mimic", "default": 0}, {"value": "reverse", "default": 0}]
			}
		]
	}
};

signature_tools = [];
$.each(tools, function(tool_name, tool){if(tool["requires_signature"]){signature_tools.push(tool_name);}})

samples = [
	{"gsm": "GSM862352", "sample_title": "LNCaP_abl_Control_KD_rep1"},
	{"gsm": "GSM862353", "sample_title": "LNCaP_abl_Control_KD_rep2"},
	{"gsm": "GSM862354", "sample_title": "LNCaP_abl_Control_KD_rep3"},
	{"gsm": "GSM862355", "sample_title": "LNCaP_abl_AR_KD_rep1"},
	{"gsm": "GSM862356", "sample_title": "LNCaP_abl_AR_KD_rep2"},
	{"gsm": "GSM862357", "sample_title": "LNCaP_abl_AR_KD_rep3"}
];

//////////////////////////////////////////////////
////////// 1. modal /////////////////////////
//////////////////////////////////////////////////

var modal = {

	Section: function(title, tool_string) {
		section = $('<div>', {'class': 'modal-section'}).html($('<span>').html(title));
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
					.append($('<input>', {'type': 'checkbox', 'class': 'modal-tool-checkbox', 'id': tool['tool_string']+'-checkbox', 'value': tool['tool_string'], 'name': 'input-tools', 'required': 'true'}))
					.append($('<label>', {'class': 'modal-tool-label', 'for': tool['tool_string']+'-checkbox'})
						.append($('<div>', {'class': 'modal-tool-icon-wrapper'})
							.html($('<img>', {'class': 'modal-tool-icon', 'src': chrome.extension.getURL('icons/'+tool['tool_string']+'.png')}))
						)
						.append($('<div>', {'class': 'modal-tool-text'})
							.append($('<div>', {'class': 'modal-tool-title'}).html(tool['tool_name']))
							.append($('<div>', {'class': 'modal-tool-description'}).html(tool['tool_description']))
						)
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
						$('<div>', {'class': 'notebook-generator-link', 'data-samples': JSON.stringify(samples), 'data-gse': gse})
							.append($('<img>', {'src': chrome.extension.getURL('icons/icon.png')}))
							.append($('<span>').html('Launch Notebook'))
					);
				}				
			})
		}			
	})
}

//////////////////////////////////////////////////
////////// 2. Add Modal //////////////////////////
//////////////////////////////////////////////////

function addModal() {
	// Add Template
	$('body').append(
		$('<div>', {'id': 'notebook-generator-modal', 'class': 'modal', 'data-gse': ''})
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
	$.ajax({
		url: "http://amp.pharm.mssm.edu/notebook-generator-server/api/tools",
		method: "POST",
		dataType: 'json',
		success: function(res) {
			$.each(res['sections'], function(index, section) {
				console.log(section);
				$('#tool-form').append(modal.Section(section['section_name']));
				$.each(section['tool_name'], function(index, tool_name) {
					$('#tool-form').append(modal.Tool(res['tools'][tool_name]));
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
	$('#notebook-generator-modal').attr('data-step', 'add-tools');
	$('#next-step').html('Next').removeClass('active');
	$('#previous-step').html('Cancel');

	// Reset Selection

	// Toggle
	$('.modal-form').hide();
	$('#tool-form').show();
}

//////////////////////////////////////////////////
////////// 4. Get Tools //////////////////////////
//////////////////////////////////////////////////

function getTools() {
	var selected_tools = [];
	$.each($('#tool-form').serializeArray(), function(i, elem) { selected_tools.push(elem['value']); });
	return selected_tools
}

//////////////////////////////////////////////////
////////// 5. Add Groups /////////////////////////
//////////////////////////////////////////////////

function addGroups() {

	// Add Text
	$('#modal-title').html('Set Groups');
	$('#notebook-generator-modal').attr('data-step', 'add-groups');
	$('#next-step').html('Next').removeClass('active');
	$('#previous-step').html('Back');

	// Add Content
	$('#group-form').html('');
	$('#group-form').append(modal.Text('One or more of the selected tools requires a gene expression signature. To proceed, complete the information below:'));
	$('#group-form').append(modal.Section('Select Samples'));
	$('#group-form').append(modal.Text('First, set the conditions by adding at least three samples per group.'));
	$('#group-form').append(modal.Table(samples));
	$('#group-form').append(modal.Section('Name Groups (optional)'));
	$('#group-form').append(modal.Text('Optionally, add a custom label for each group.'));
	$('#group-form').append(modal.Input('Group A:', 'Label to assign to Group A', 'group_a'));
	$('#group-form').append(modal.Input('Group B:', 'Label to assign to Group B', 'group_a'));

	// Toggle
	$('.modal-form').hide();
	$('#group-form').show();
}

//////////////////////////////////////////////////
////////// 6. Get Groups /////////////////////////
//////////////////////////////////////////////////

function getGroups() {
	
	// Set Variables
	var groups = {'A': {'name': '', 'samples': []}, 'B': {'name': '', 'samples': []}}, form=$('#group-form').serializeArray();

	// Add labels
	$.each(form, function(index, elem) {
		var name = elem['name'], value = elem['value'];

		// Group labels
		if (['group_a', 'group_b'].indexOf(name) > -1 ) {
			var group = name.split('_')[1].toUpperCase();
			groups[group]['name'] = value;
		} else {
			// Sample labels
			groups[value]['samples'].push(name);
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
	$('#notebook-generator-modal').attr('data-step', 'add-configuration');
	$('#previous-step').html('Back');
	$('#next-step').html('Get Notebook').addClass('active');

	// Add Content
	$('#configuration-form').html('');
	$('#configuration-form').append(modal.Text('Optionally, review the notebook and modify optional parameters:'));
	$('#configuration-form').append(modal.Section('General Settings'));
	$('#configuration-form').append(modal.Input('Notebook Title:', 'Title of the Jupyter Notebook', 'notebook_title', $('#notebook-generator-modal').attr('data-gse')+' Analysis Notebook'));
	$('#configuration-form').append(modal.Input('Live:', 'Indicates whether the Jupyter Notebook should be deployed in a live server or as a static HTML report', 'live', 'False', 'select', ['False', 'True']));

	// Add Tool Parameters
	$.each(selected_tools, function(index, tool_string){
		var parameters = tools[tool_string]['parameters'];
		if (parameters.length > 0) {
			$('#configuration-form').append(modal.Section(tools[tool_string]["tool_name"], tool_string));
			$.each(parameters, function(parameter_id, parameter) {
				var value, options = [];
				$.each(parameter['values'], function(index, option) { options.push(option["value"]); if (option["default"]){value = option["value"]}; });
				$('#configuration-form').append(modal.Input(parameter["parameter_name"]+' :', parameter["parameter_description"], parameter["parameter_string"], value, 'select', options));
			})
		}
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
	var current_tool, configuration = {'general':{}, 'tools':{}};

	// Serialize form
	form = $('#configuration-form').serializeArray();

	// Loop through form
	$.each(form, function(index, parameter) {

		// Add general parameters
		if (['notebook_title', 'live'].indexOf(parameter['name']) > -1) {
			configuration['general'][parameter['name']] = parameter['value'];
		}

		// Get current tool
		if (parameter['name'] === 'tool_string') {
			current_tool = parameter['value'];
			configuration['tools'][current_tool] = {};
 		}

		// Add tool parameters
		if (current_tool && parameter['name'] != 'tool_string') {
			configuration['tools'][current_tool][parameter['name']] = parameter['value'];
		}

	})

	// Return
	return configuration
}

//////////////////////////////////////////////////
////////// 9. Get Notebook Link //////////////////
//////////////////////////////////////////////////

function addNotebookLink(configuration) {
	// $.ajax();
	// Ajax
	// wait(5000);
	$('.sk-circle').remove();
	$('#modal-loading-text').html('Your Notebook is available at the link below:')
	$('#results-form').append($('<div>', {'id': 'modal-notebook-results'}).html($('<a>', {'id': 'modal-notebook-link', 'href': 'http://www.google.com', 'target': '_blank'}).html('Open Notebook')));

}

function wait(ms){
   var start = new Date().getTime();
   var end = start;
   while(end < start + ms) {
     end = new Date().getTime();
  }
}

//////////////////////////////////////////////////
////////// 10. Add Notebook //////////////////////
//////////////////////////////////////////////////

function showNotebookForm() {
	// Add Text
	$('#modal-title').html('Results');
	$('#next-step').html('Done').addClass('active');
	$('#notebook-generator-modal').attr('data-step', 'results');
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
	var step, selected_tools, groups, configuration;

	// open modal
	$(document).on('click', '.notebook-generator-link', function() {
		$('#notebook-generator-modal').css('display', 'block');
		addTools();
	})

	// close modal
	$(document).click(function(evt) {
		if ($(evt.target).attr('id') === 'notebook-generator-modal' ) {
			$('#notebook-generator-modal').css('display', 'none');
			$('#notebook-generator-modal form').css('display', 'none');
		}
	})

	// Next step
	$('#next-step').click(function(evt) {
		var step = $('#notebook-generator-modal').attr('data-step');

		// Add Tools Step
		if (step === 'add-tools') {

			// Get Tools
			selected_tools = getTools();

			// If no tools selected
			if (selected_tools.length === 0) {
				alert('Please select one or more tools to continue.')
			} else {

				// If tools require signature
				if (selected_tools.some(a => signature_tools.some( m => a === m))) {
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
			$.each(groups, function(key, value) { if (value['samples'].length < 3) { small_groups.push(key) } })

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
			if (groups) {
				configuration['groups'] = groups;
			}

			// Get Notebook
			showNotebookForm();
			addNotebookLink(configuration);

		}

		// Results
		else if (step === 'results') {
			// Close modal
			$('#notebook-generator-modal').click();
		}

		// De-focus Button
		$(evt.target).blur();
	})

	// Previous Step
	$('#previous-step').click(function(evt) {

		// Get Step
		var step = $('#notebook-generator-modal').attr('data-step');

		// Toggle Forms
		$('.modal-form').hide();

		// Add Tools
		if (step === 'add-tools') {
			$('#notebook-generator-modal').click();
		} else if (step === 'add-groups') {
			$('#tool-form').show();
			$('#notebook-generator-modal').attr('data-step', 'add-tools');
			$('#previous-step').html('Cancel').removeClass('active');
		} else if (step === 'add-configuration') {
			// If Groups are required
			if (selected_tools.some(a => signature_tools.some( m => a === m))) {
				$('#group-form').show();
				$('#notebook-generator-modal').attr('data-step', 'add-groups');
				$('#previous-step').html('Back').removeClass('active');
				$('#next-step').html('Next');
			// If groups aren't required
			} else {
				$('#tool-form').show();
				$('#notebook-generator-modal').attr('data-step', 'add-tools');
				$('#previous-step').html('Cancel');
				$('#next-step').html('Next');
			}
		} else if (step === 'results') {
			$('#results-form').hide();
			$('#configuration-form').show();
			$('#notebook-generator-modal').attr('data-step', 'add-configuration');
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
