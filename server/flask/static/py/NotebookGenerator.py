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

#############################################
########## 2. Variables
#############################################
##### 1. Helper Function #####
def addCell(notebook, content, celltype='code'):
	if celltype == 'code':
		notebook['cells'].append(nbf.v4.new_code_cell(content))
	elif celltype == 'markdown':
		notebook['cells'].append(nbf.v4.new_markdown_cell(content))
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
########## 2. Add Intro
#############################################

def add_intro(notebook, notebook_configuration, tool_metadata):

	# Get Sections
	sections = [{'id': 'load_dataset', 'name': 'Load Dataset', 'description': 'Load and preview the input dataset in the notebook environment.'}]
	if len(set([tool_configuration['parameters']['normalization'] for tool_configuration in notebook_configuration['tools'] if 'normalization' in tool_configuration['parameters'].keys()])):
		sections.append({'id': 'normalize_dataset', 'name': 'Normalize Dataset', 'description': 'Normalize the dataset prior to downstream analysis.'})
	if len(notebook_configuration['signature']):
		sections.append({'id': 'generate_signature', 'name': 'Generate Signature', 'description': 'Generate differential gene expression signatures by comparing gene expression between two groups.'})
	for tool_configuration in notebook_configuration['tools']:
		tool_meta = tool_metadata[tool_configuration['tool_string']]
		sections.append({'id': tool_configuration['tool_string'], 'name': tool_meta['tool_name'], 'description': tool_meta['tool_description']})
	sections_str = ''.join(['<li><b><a href="#{id}">{name}</a></b> - <i>{description}</i></li>'.format(**x) for x in sections])

	# Add Intro
	cell = """# {notebook[title]}\n ## Overview\nThis notebook contains an analyis of GEO dataset {data[parameters][gse]} (https://www.ncbi.nlm.nih.gov/gds/?term={data[parameters][gse]}) generated using the Jupyter Notebook Generator.""".format(**notebook_configuration) + \
			"""\n### Sections\nThe analysis is divided in the following sections:\n<ol>{}</ol>""".format(sections_str)
	return addCell(notebook, cell, 'markdown')

#############################################
########## 3. Load Data
#############################################

def load_data(notebook, data_configuration):

	# Section
	global section_nr
	section_nr = 1
	
	# Intro text
	cell = "---\n # <span id='load_dataset'>1. Load Dataset</span>\nFirst, the RNA-seq dataset is loaded in the Jupyter Environment from the ARCHS4 resource (http://amp.pharm.mssm.edu/archs4/)."
	notebook = addCell(notebook, cell, 'markdown')

	# Add Data
	cell = "# Load dataset\ndataset = load_dataset(source='{}'".format(data_configuration['source'])+add_parameters(data_configuration['parameters'])+")\n\n# Preview expression data\ndataset['rawdata'].head()"
	notebook = addCell(notebook, cell)
	cell = "**Table 1 | RNA-seq expression data.** The table displays the first 5 rows of the quantified RNA-seq expression dataset.  Rows represent genes, columns represent samples, and values show the number of mapped reads."
	notebook = addCell(notebook, cell, 'markdown')

	# Add Metadata
	cell = "# Display metadata\ndataset['sample_metadata']"
	notebook = addCell(notebook, cell)
	cell = "**Table 2 | Sample metadata.** The table displays the metadata associated to the samples in the RNA-seq dataset.  Rows represent RNA-seq samples, columns represent metadata categories."
	return addCell(notebook, cell, 'markdown')

#############################################
########## 4. Normalize Data
#############################################

def normalize_data(notebook, normalization_methods):

	# # Section
	# global section_nr
	# section_nr += 1

	# # Intro text
	# cell = "---\n # <span id='normalize_data'>{section_nr}. Normalize Data</span>\nHere the RNA-seq data is normalized in preparation for downstream analysis.".format(**globals()) + "The following methods are used:<ul>"+''.join(['<li>{}</li>'.format(x) for x in normalization_methods])+"</ul>"
	# notebook = addCell(notebook, cell, 'markdown')

	# Loop through methods
	for normalization_method in normalization_methods:
		cell = "# Normalize dataset\ndataset['{normalization_method}'] = normalize_dataset(dataset=dataset, method='{normalization_method}')".format(**locals())
		notebook = addCell(notebook, cell)

	return notebook

#############################################
########## 5. Generate Signature
#############################################

def generate_signature(notebook, signature_configuration):

	# Section
	global section_nr
	section_nr += 1

	# Intro text
	cell = "---\n # <span id='generate_signature'>{section_nr}. Generate Signature</span>\nHere a differential gene expression signature is generated by comparing the two groups ".format(**globals()) + "using <i>{method}</i>. <ul><li><b>{A[name]}</b>: <i>{A[samples]}</i></li><li><b>{B[name]}</b>: <i>{B[samples]}</i></li></ul>".format(**signature_configuration).replace("['", '').replace("']", '').replace("', '", ', ')
	notebook = addCell(notebook, cell, 'markdown')

	# Generate Signature
	cell = "# Configure signatures\nsignature_metadata = {{\n    '{A[name]} vs {B[name]}': {{'A': {A[samples]}, 'B': {B[samples]}}}\n}}\n\n# Generate signatures\nfor label, groups in signature_metadata.items():\n    signatures[label] = generate_signature(group_A=groups['A'], group_B=groups['B'], method='{method}', dataset=dataset)".format(**signature_configuration)
	return addCell(notebook, cell)

#############################################
########## 6. Add Tool
#############################################

def add_tool(notebook, tool_configuration, tool_metadata):

	# Section
	global section_nr
	section_nr += 1

	# Intro text
	cell = "---\n # <span id='{}'>".format(tool_configuration['tool_string'])+str(section_nr)+". {tool_name}</span>\n{tool_notebook_annotation}".format(**tool_metadata[tool_configuration['tool_string']])
	notebook = addCell(notebook, cell, 'markdown')

	# Add Tool
	if tool_metadata[tool_configuration['tool_string']]['requires_signature']:
		cell = "# Initialize results\nresults['{tool_string}'] = {{}}\n\n# Loop through signatures\nfor label, signature in signatures.items():\n\n    # Run analysis\n    results['{tool_string}'][label] = analyze(signature=signature, tool='{tool_string}', signature_label=label".format(**tool_configuration)+add_parameters(tool_configuration['parameters'])+")\n\n    # Display results\n    plot(results['{tool_string}'][label])".format(**tool_configuration)
	else:
		cell = "# Run analysis\nresults['{tool_string}'] = analyze(dataset=dataset, tool='{tool_string}'".format(**tool_configuration)+add_parameters(tool_configuration['parameters'])+")\n\n# Display results\nplot(results['{tool_string}'])".format(**tool_configuration)
	return addCell(notebook, cell)

#############################################
########## 7. Add Footer
#############################################

def add_footer(notebook):

	# Add Footer
	cell = "---\n<div style='text-align: center;'>The Jupyter Notebook Generator is being developed by the Ma'ayan Lab at the Icahn School of Medicine at Mount Sinai<br>and is an open source project available on <a href='https://github.com/denis-torre/notebook-generator'>GitHub</a>.</div>"
	return addCell(notebook, cell, 'markdown')

#################################################################
#################################################################
############### 2. Wrapper ######################################
#################################################################
#################################################################

#############################################
########## 1. Generate Notebook
#############################################

def generate_notebook(notebook_configuration, tool_metadata):

	# Create Notebook
	notebook = nbf.v4.new_notebook()

	# Initialize Notebook
	notebook['cells'].append(nbf.v4.new_code_cell("""# Initialize Notebook\n%run """+notebook_configuration['notebook']['version']+"""/init.ipy\nHTML('''<script> code_show=true;  function code_toggle() {  if (code_show){  $('div.input').hide();  } else {  $('div.input').show();  }  code_show = !code_show }  $( document ).ready(code_toggle); </script> <form action="javascript:code_toggle()"><input type="submit" value="Toggle Code"></form>''')"""))
	
	# Add Intro
	notebook = add_intro(notebook=notebook, notebook_configuration=notebook_configuration, tool_metadata=tool_metadata)

	# Load Data
	notebook = load_data(notebook=notebook, data_configuration=notebook_configuration['data'])

	# Normalize Data
	normalization_methods = set([tool_configuration['parameters']['normalization'] for tool_configuration in notebook_configuration['tools'] if 'normalization' in tool_configuration['parameters'].keys() and tool_configuration['parameters']['normalization'] != 'rawdata'])
	if normalization_methods:
		notebook = normalize_data(notebook=notebook, normalization_methods=normalization_methods)

	# Generate Signature
	if len(notebook_configuration['signature']):
		notebook = generate_signature(notebook=notebook, signature_configuration=notebook_configuration['signature'])

	# Add Tools
	for tool_configuration in notebook_configuration['tools']:
		notebook = add_tool(notebook=notebook, tool_configuration=tool_configuration, tool_metadata=tool_metadata)

	# Add Footer
	notebook = add_footer(notebook)

	# Return
	return notebook