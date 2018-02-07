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
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config

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

##### 2. Notebook Execution #####
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

##### 3. Notebook Conversion #####
c = Config()
c.HTMLExporter.preprocessors = ['nbconvert.preprocessors.ExtractOutputPreprocessor']
html_exporter_with_figs = HTMLExporter(config=c)

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

def generate_signature(notebook, signature_configuration):
	# Generate Signature
	cell = "# Configure signature\ngroup_A = {A[samples]} # {A[name]}\ngroup_B = {B[samples]} # {B[name]}\nsignature_method = '{method}'\n\n# Generate signature\nsignature = generate_signature(group_A=group_A, group_B=group_B, method=signature_method, dataset=dataset)\nsignature.head()".format(**signature_configuration)
	return addCell(notebook, cell)

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
	# notebook['cells'].append(nbf.v4.new_code_cell("""# Initialize Notebook\n%run static/library/"""+notebook_configuration['notebook']['version']+"""/init.ipy\nHTML('''<script> code_show=true;  function code_toggle() {  if (code_show){  $('div.input').hide();  } else {  $('div.input').show();  }  code_show = !code_show }  $( document ).ready(code_toggle); </script> <form action="javascript:code_toggle()"><input type="submit" value="Toggle Code"></form>''')"""))

	# Load Data
	notebook = load_data(notebook=notebook, data_configuration=notebook_configuration['data'])

	# Normalize Data
	notebook = normalize_data(notebook=notebook, tool_configuration_list=notebook_configuration['tools'])

	# Generate Signature
	if len(notebook_configuration['signature']):
		notebook = generate_signature(notebook=notebook, signature_configuration=notebook_configuration['signature'])

	# Add Tools
	for tool_configuration in notebook_configuration['tools']:
		notebook = add_tool(notebook=notebook, tool_configuration=tool_configuration)

	# Return
	return notebook

#############################################
########## 2. Execute Notebook
#############################################

def execute_notebook(notebook, notebook_title):

	# Execute
	ep.preprocess(notebook, {'metadata': {'path': '.'}})

	# Convert
	notebook_html = html_exporter_with_figs.from_notebook_node(notebook)[0]

	# Add title
	notebook_html = notebook_html.replace('<title>Notebook</title>', '<title>{}</title>'.format(notebook_title))

	# Return
	return notebook_html

