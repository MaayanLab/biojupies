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
########## 2. Load Data
#############################################

def load_data(notebook, data_configuration):
	# Add Data and Display Metadata
	cell = "# Load dataset\ndataset = load_dataset(source='{}'".format(data_configuration['source'])+add_parameters(data_configuration['parameters'])+")\n\n# Preview expression data\ndataset['rawdata'].head()"
	notebook = addCell(notebook, cell)
	cell = "# Display metadata\ndataset['sample_metadata']"
	return addCell(notebook, cell)

#############################################
########## 3. Normalize Data
#############################################

def normalize_data(notebook, tool_configuration_list):
	# Get Normalization Methods
	normalization_methods = set([tool_configuration['parameters']['normalization'] for tool_configuration in tool_configuration_list if 'normalization' in tool_configuration['parameters'].keys()])
	for normalization_method in normalization_methods:
		cell = "# Normalize dataset\ndataset['{normalization_method}'] = normalize_dataset(dataset=dataset, method='{normalization_method}')".format(**locals())
		notebook = addCell(notebook, cell)
	return notebook

#############################################
########## 4. Generate Signature
#############################################

def generate_signatures(notebook, signature_configuration):
	# Generate Signature
	config_cell = "# Configure signatures\nsignatures_metadata = {{\n    '{A[name]} vs {B[name]}': {{'{A[name]}': {A[samples]}, '{B[name]}': {B[samples]}}}\n}}".format(**signature_configuration)
	compute_cell = "# Generate signatures\nfor signature_label, groups in signature_metadata.items():\n    signatures[signature_label] = compute_signature(group_A=groups['A'], group_B=groups['B'], method='{}')".format(signature_configuration['method'])
	return addCell(addCell(notebook, config_cell), compute_cell)

#############################################
########## 5. Add Tool
#############################################

def add_tool(notebook, tool_configuration):
	# Add Tool
	cell = "# Run analysis\nresults['{tool_string}'] = analyze({tool_input}={tool_input}, tool='{tool_string}'".format(**tool_configuration)+add_parameters(tool_configuration['parameters'])+")\n\n# Display results\nplot(results['{tool_string}'])".format(**tool_configuration)
	return addCell(notebook, cell)

#################################################################
#################################################################
############### 2. Wrapper ######################################
#################################################################
#################################################################

#############################################
########## 1. Generate Notebook
#############################################

def generate_notebook(notebook_configuration):

	# Create Notebook
	notebook = nbf.v4.new_notebook()

	# Initialize Notebook
	# notebook['cells'].append(nbf.v4.new_code_cell("""# Initialize Notebook\n%run """+notebook_configuration['notebook']['version']+"""/init.ipy\nHTML('''<script> code_show=true;  function code_toggle() {  if (code_show){  $('div.input').hide();  } else {  $('div.input').show();  }  code_show = !code_show }  $( document ).ready(code_toggle); </script> <form action="javascript:code_toggle()"><input type="submit" value="Toggle Code"></form>''')"""))

	# Load Data
	notebook = load_data(notebook=notebook, data_configuration=notebook_configuration['data'])

	# Normalize Data
	notebook = normalize_data(notebook=notebook, tool_configuration_list=notebook_configuration['tools'])

	# Generate Signature
	if len(notebook_configuration['signature']):
		notebook = generate_signatures(notebook=notebook, signature_configuration=notebook_configuration['signature'])

	# Add Tools
	for tool_configuration in notebook_configuration['tools']:
		notebook = add_tool(notebook=notebook, tool_configuration=tool_configuration)

	# Return
	return notebook