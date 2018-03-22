#################################################################
#################################################################
############### Notebook Generator API ##########################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#################################################################
#################################################################
############### 1. Library Configuration ########################
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. Python modules #####
import nbformat as nbf
import pandas as pd

#############################################
########## 2. Variables
#############################################
##### 1. Helper Function #####
def addCell(notebook, content, celltype='code', task=None):
	if celltype == 'code':
		cell = nbf.v4.new_code_cell(content)
	elif celltype == 'markdown':
		cell = nbf.v4.new_markdown_cell(content)
	if task:
		cell.metadata.update({'task': task})
	notebook['cells'].append(cell)
	return notebook

#################################################################
#################################################################
############### 1. Functions ####################################
#################################################################
#################################################################

#############################################
########## 1. Add Parameters
#############################################

def add_parameters(configuration_dict):
	parameters = ", " if len(configuration_dict) else ""
	return parameters+", ".join(['='.join([str(key), str(value) if str(value).isnumeric() or not value else "'"+str(value)+"'"]) for key, value in configuration_dict.items()])

#############################################
########## 2. Add Introduction
#############################################

def add_introduction(notebook, notebook_configuration, tool_metadata):

	# Get Sections
	sections = [{'id': 'load_dataset', 'name': 'Load Dataset', 'description': 'Loads and previews the input dataset in the notebook environment.'}]
	# if len(set([tool_configuration['parameters']['normalization'] for tool_configuration in notebook_configuration['tools'] if 'normalization' in tool_configuration['parameters'].keys()])):
		# sections.append({'id': 'normalize_dataset', 'name': 'Normalize Dataset', 'description': 'Normalize the dataset prior to downstream analysis.'})
	# if len(notebook_configuration['signature']):
		# sections.append({'id': 'generate_signature', 'name': 'Generate Signature', 'description': 'Generates differential gene expression signatures by comparing gene expression between the two groups.'})
	for tool_configuration in notebook_configuration['tools']:
		tool_meta = tool_metadata[tool_configuration['tool_string']]
		sections.append({'id': tool_configuration['tool_string'], 'name': tool_meta['tool_name'], 'description': tool_meta['tool_description']})
	sections_str = ''.join(['<li><b><a href="#{id}">{name}</a></b> - <i>{description}</i></li>'.format(**x) for x in sections])

	# Add Intro
	if 'gse' in notebook_configuration['data']['parameters'].keys():
		cell = """# {notebook[title]}\n---\n# Introduction\nThis notebook contains an analyis of GEO dataset {data[parameters][gse]} (https://www.ncbi.nlm.nih.gov/gds/?term={data[parameters][gse]}) created using the BioJupies Generator.""".format(**notebook_configuration)
	else:
		cell = """# {notebook[title]}\n---\n# Introduction\nThis notebook contains an analyis of a user-submitted dataset created using the BioJupies Generator.""".format(**notebook_configuration)
	cell += """\n### Table of Contents\nThe notebook is divided into the following sections:\n<ol>{}</ol>""".format(sections_str)
	return addCell(notebook, cell, 'markdown')

#############################################
########## 3. Load Data
#############################################

def load_data(notebook, data_configuration, core_options):

	# Section
	global section_nr
	section_nr = 1
	
	# Intro text
	cell = "---\n# Results\n## <span id='load_dataset'>1. Load Dataset</span>\n"+core_options[data_configuration['source']]['introduction'].format(**data_configuration['parameters'])
	notebook = addCell(notebook, cell, 'markdown', 'load_dataset')

	# Add Data
	cell = "# Load dataset\ndataset = load_dataset(source='{}'".format(data_configuration['source'])+add_parameters(data_configuration['parameters'])+")\n\n# Preview expression data\ndataset['rawdata'].head()"
	notebook = addCell(notebook, cell)
	cell = "**Table 1 | RNA-seq expression data.** The table displays the first 5 rows of the quantified RNA-seq expression dataset.  Rows represent genes, columns represent samples, and values show the number of mapped reads."
	notebook = addCell(notebook, cell, 'markdown')

	# Add Metadata
	cell = "# Display metadata\ndataset['sample_metadata']"
	notebook = addCell(notebook, cell)
	cell = "**Table 2 | Sample metadata.** The table displays the metadata associated with the samples in the RNA-seq dataset.  Rows represent RNA-seq samples, columns represent metadata categories."
	return addCell(notebook, cell, 'markdown')

#############################################
########## 4. Generate Signature
#############################################

def generate_signature(notebook, signature_configuration, core_options):

	# Section
	# global section_nr
	# section_nr += 1

	# Get signature dataframe
	# signature_dataframe = pd.DataFrame(signature_configuration).T.drop('method').rename(columns={'name': 'Group', 'samples': 'Samples'})
	# signature_dataframe['Samples'] = [', '.join(x) for x in signature_dataframe['Samples']]
	# pd.set_option('max.colwidth', -1)
	# signature_table= signature_dataframe.to_html(index=False)

	# Intro text
	# cell = "---\n ## <span id='generate_signature'>{section_nr}. Generate Signature</span>\nHere, differential gene expression analysis is performed in order to identify a signature by comparing the following two groups:".format(**globals()) + "<br>{}".format(signature_table)
	# cell += core_options[signature_configuration['method']]['introduction'].format(**signature_configuration)
	# notebook = addCell(notebook, cell, 'markdown')

	# Generate Signature
	cell = "# Configure signatures\ndataset['signature_metadata'] = {{\n    '{A[name]} vs {B[name]}': {{\n        'A': {A[samples]},\n        'B': {B[samples]}\n    }}\n}}\n\n# Generate signatures\nfor label, groups in dataset['signature_metadata'].items():\n    signatures[label] = generate_signature(group_A=groups['A'], group_B=groups['B'], method='{method}', dataset=dataset)".format(**signature_configuration)
	return addCell(notebook, cell, task='generate_signature')

#############################################
########## 5. Add Tool
#############################################

def add_tool(notebook, tool_configuration, tool_metadata, signature_configuration, annotate=True):

	# Get Tool input
	tool_string = tool_configuration['tool_string']
	tool_input = tool_metadata[tool_string]['input']

	# Markdown annotation
	if annotate:

		# Section
		global section_nr
		section_nr += 1

		# Intro text
		cell = "---\n ## <span id='{}'>".format(tool_string)+str(section_nr)+". {tool_name}</span>\n".format(**tool_metadata[tool_string])+tool_metadata[tool_string]['introduction'].format(**signature_configuration, **tool_configuration['parameters'])#+annotations[tool_configuration['tool_string']]['introduction']
		notebook = addCell(notebook, cell, 'markdown')

	# Tools with dataset input
	if tool_input == 'dataset':
		cell = "# Run analysis\nresults['{tool_string}'] = analyze(dataset=dataset, tool='{tool_string}'".format(**tool_configuration)+add_parameters(tool_configuration['parameters'])+")"
		if annotate:
			cell += "\n\n# Display results\nplot(results['{tool_string}'])".format(**tool_configuration)

	# Tools with signature input
	elif tool_input == 'signature':
		cell = "# Initialize results\nresults['{tool_string}'] = {{}}\n\n# Loop through signatures\nfor label, signature in signatures.items():\n\n    # Run analysis\n    results['{tool_string}'][label] = analyze(signature=signature, tool='{tool_string}', signature_label=label".format(**tool_configuration)+add_parameters(tool_configuration['parameters'])+")"
		if annotate:
			cell += "\n\n    # Display results\n    plot(results['{tool_string}'][label])".format(**tool_configuration)

	# Tools with other tools as input
	else:

		# Add prerequisite
		notebook = add_tool(notebook, {'tool_string': tool_input, 'parameters': {}}, tool_metadata, signature_configuration, annotate=False)

		# Add tool
		if tool_metadata[tool_input]['input'] == 'signature':
			tool_configuration.update({'tool_input': tool_input})
			cell = "# Initialize results\nresults['{tool_string}'] = {{}}\n\n# Loop through results\nfor label, {tool_input}_results in results['{tool_input}'].items():\n\n    # Run analysis\n    results['{tool_string}'][label] = analyze({tool_input}_results={tool_input}_results['results'], tool='{tool_string}', signature_label=label".format(**tool_configuration)+add_parameters(tool_configuration['parameters'])+")\n\n    # Display results\n    plot(results['{tool_string}'][label])".format(**tool_configuration)
		else:
			cell = "# Run analysis\nresults['{tool_string}'] = analyze({tool_input}_results=results['{tool_input}']['results']".format(**locals())+", tool='{tool_string}'".format(**tool_configuration)+add_parameters(tool_configuration['parameters'])+")\n\n# Display results\nplot(results['{tool_string}'])".format(**tool_configuration)
	return addCell(notebook, cell, task=tool_configuration['tool_string'])

#############################################
########## 6. Add Methods
#############################################

def add_methods(notebook, notebook_configuration, normalization_methods, annotations):

	# Initialize Methods
	methods = []

	# Add Data Methods
	data_configuration = notebook_configuration['data']
	data_methods = '### Data Processing\n'+annotations['core_options'][data_configuration['source']]['methods'].format(**data_configuration['parameters'])
	methods.append(data_methods)

	# Add Signature Methods
	if len(notebook_configuration['signature']):
		signature_configuration = notebook_configuration['signature']
		signature_methods = '### Signature Generation\n'+annotations['core_options'][signature_configuration['method']]['methods'].format(**signature_configuration)
		methods.append(signature_methods)

	# Add Normalization Methods
	if len(normalization_methods):
		normalization_methods_section = '### Data Normalization\n'
		for normalization_method in normalization_methods:
			normalization_methods_section += '##### {}\n'.format(annotations['core_options'][normalization_method]['option_name'])+annotations['core_options'][normalization_method]['methods']
		# normalization_methods_section += '<br><br>Source code and additional information is available on GitHub: <a href="https://github.com/denis-torre/notebook-generator/tree/master/library/{notebook_configuration[notebook][version]}/core_scripts/normalize" target="_blank">https://github.com/denis-torre/notebook-generator/tree/master/library/{notebook_configuration[notebook][version]}/core_scripts/normalize</a>.'.format(**locals())
		# normalization_methods_section += '<br><br>Source code and additional information are publicly available on <a href="https://github.com/denis-torre/notebook-generator/tree/master/library/{notebook_configuration[notebook][version]}/core_scripts/normalize" target="_blank">GitHub</a>.'.format(**locals())
		methods.append(normalization_methods_section)

	# Add Tool Methods
	for tool_configuration in notebook_configuration['tools']:
		selected_tool_metadata = annotations['tools'][tool_configuration['tool_string']]
		if selected_tool_metadata['methods']:
			tool_method = '### {selected_tool_metadata[tool_name]}\n'.format(**locals())+selected_tool_metadata['methods'].format(**tool_configuration['parameters'])#+'<br><br>Source code and additional information are publicly available on <a href="https://github.com/denis-torre/notebook-generator/tree/master/library/{notebook_configuration[notebook][version]}/analysis_tools/{tool_configuration[tool_string]}" target="_blank">GitHub</a>.'.format(**locals())
			methods.append(tool_method)
			# methods.append(annotations['tools'][tool_configuration['tool_string']]['methods'].format(**tool_configuration['parameters']))

	# Join
	cell = "---\n# <span id='methods'>Methods</span>\n"+'\n\n'.join(methods)
	return addCell(notebook, cell, 'markdown')

#############################################
########## 7. Add References
#############################################

def add_references(notebook, notebook_configuration, normalization_methods, annotations):

	# Add References
	tool_references = pd.DataFrame([annotations['tools'][x['tool_string']] for x in notebook_configuration['tools']])
	core_options_references = pd.DataFrame([annotations['core_options'][x] for x in [notebook_configuration['data']['source'], notebook_configuration['signature'].get('method')]+list(normalization_methods) if x in annotations['core_options'].keys()])
	references_dataframe = pd.concat([tool_references, core_options_references]).drop_duplicates('reference').sort_values('reference').drop_duplicates('reference')
	references_dataframe['id'] = [x.split('.org/')[-1] for x in references_dataframe['reference_link']]
	cell = "---\n## <span id='references'>References</span>\n"+'<br>'.join(['{reference} doi: <a id="{id}" href="{reference_link}" target="_blank">{reference_link}</a><br>'.format(**rowData) for index, rowData in references_dataframe.iterrows() if rowData['reference']])
	return addCell(notebook, cell, 'markdown')

#############################################
########## 8. Add Footer
#############################################

def add_footer(notebook):

	# Add Footer
	# cell = "---\n<div style='text-align: center;'>The Jupyter Notebook Generator is being developed by the Ma'ayan Lab at the Icahn School of Medicine at Mount Sinai<br>and is an open source project available on <a href='https://github.com/denis-torre/notebook-generator'>GitHub</a>.</div>"
	cell = "---\n<div style='text-align: center;'>The Jupyter Notebook Generator is being developed by the <a href='http://icahn.mssm.edu/research/labs/maayan-laboratory' target='_blank'>Ma'ayan Lab</a> at the <a href='http://icahn.mssm.edu/' target='_blank'>Icahn School of Medicine at Mount Sinai</a><br>and is an open source project available on <a href='https://github.com/denis-torre/notebook-generator'>GitHub</a>.</div>"

	return addCell(notebook, cell, 'markdown')

#################################################################
#################################################################
############### 2. Wrapper ######################################
#################################################################
#################################################################

#############################################
########## 1. Generate Notebook
#############################################

def generate_notebook(notebook_configuration, annotations):

	# Create Notebook
	notebook = nbf.v4.new_notebook()

	# Initialize Notebook
	notebook['cells'].append(nbf.v4.new_code_cell("""# Initialize Notebook\n%run """+notebook_configuration['notebook']['version']+"""/init.ipy\nHTML('''<script> code_show=true;  function code_toggle() {  if (code_show){  $('div.input').hide();  } else {  $('div.input').show();  }  code_show = !code_show }  $( document ).ready(code_toggle); </script> <form action="javascript:code_toggle()"><input type="submit" value="Toggle Code"></form>''')"""))
	
	# Add Intro
	notebook = add_introduction(notebook=notebook, notebook_configuration=notebook_configuration, tool_metadata=annotations['tools'])

	# Load Data
	notebook = load_data(notebook=notebook, data_configuration=notebook_configuration['data'], core_options=annotations['core_options'])

	# Generate Signature
	if len(notebook_configuration['signature']):
		notebook = generate_signature(notebook=notebook, signature_configuration=notebook_configuration['signature'], core_options=annotations['core_options'])

	# Add Tools
	for tool_configuration in notebook_configuration['tools']:
		notebook = add_tool(notebook=notebook, tool_configuration=tool_configuration, tool_metadata=annotations['tools'], signature_configuration=notebook_configuration['signature'])

	# Add Methods
	normalization_methods = set([tool_configuration['parameters']['normalization'] for tool_configuration in notebook_configuration['tools'] if 'normalization' in tool_configuration['parameters'].keys() and tool_configuration['parameters']['normalization'] != 'rawdata'])
	notebook = add_methods(notebook, notebook_configuration=notebook_configuration, normalization_methods=normalization_methods, annotations=annotations)

	# Add References
	notebook = add_references(notebook, notebook_configuration=notebook_configuration, normalization_methods=normalization_methods, annotations=annotations)

	# Add Footer
	notebook = add_footer(notebook)

	# Return
	return notebook