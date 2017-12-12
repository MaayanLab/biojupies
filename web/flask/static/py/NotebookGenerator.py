#################################################################
#################################################################
############### Notebook Generator ##############################
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

#################################################################
#################################################################
############### 1. Notebook Generation ##########################
#################################################################
#################################################################

#############################################
########## 1. Generate Notebook
#############################################

def AddCodeCell(notebook, content, init=True):
	notebook['cells'].append(nbf.v4.new_code_cell(content))
	notebook['cells'][-1].metadata.init_cell=True
	notebook['cells'][-1].metadata.hide_input=True

def BaseNotebook(dataset_accession):

	# Create new notebook
	notebook = nbf.v4.new_notebook()

	# Get Toggle Code
	toggle_code = """from IPython.display import HTML
HTML('''<script>
code_show=true; 
function code_toggle() {
 if (code_show){
 $('div.input').hide();
 } else {
 $('div.input').show();
 }
 code_show = !code_show
} 
$( document ).ready(code_toggle);
</script>
<form action="javascript:code_toggle()"><input type="submit" value="Toggle Code"></form>''')"""

	# Get Intro Text
	intro_text = """
# {dataset_accession} Analysis Notebook
## Overview
##### Introduction
This Notebook contains an analysis of GEO dataset [{dataset_accession}](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={dataset_accession}).  It has been programmatically generated with the Jupyter Notebook Generator, available at the following [link](https://amp.pharm.mssm.edu/notebook-generator-web/notebook?acc={dataset_accession}).

##### Sections
The report is divided in two sections:

1. *Data Processing*. This section covers the process of download and preprocessing of the dataset.
2. *Data Analysis*. This section covers the application of scripts and computational tools to analyze the dataset.

## 1. Data Processing
Here we download the dataset from the ARCHS4 library, load data and metadata in pandas DataFrames.
	""".format(**locals())

	# Load Libraries
	AddCodeCell(notebook, toggle_code)
	notebook['cells'].append(nbf.v4.new_markdown_cell(intro_text))
	AddCodeCell(notebook, '# Initialize Notebook\n%run ../scripts/nb.ipy')

	# Fetch Data
	AddCodeCell(notebook, '# Get Dataset\nrawcount_dataframe, sample_metadata_dataframe = fetch_dataset("{dataset_accession}")\nrawcount_dataframe.head()'.format(**locals()))
	AddCodeCell(notebook, '# Show Metadata\nsample_metadata_dataframe'.format(**locals()))

	# Data Analysis
	notebook['cells'].append(nbf.v4.new_markdown_cell('## 2. Data Analysis'))

	# Return
	return notebook


def AddAnalyses(notebook, toolkit_id):

	if toolkit_id == 1:
		return notebook
	elif toolkit_id == 2:
		AddCodeCell(notebook, 'plot_library_sizes(rawcount_dataframe);')
		AddCodeCell(notebook, 'plot_library_sizes(rawcount_dataframe);')


def GenerateNotebook(notebook_configuration):

	# Get Notebook
	notebook = BaseNotebook(dataset_accession=notebook_configuration['dataset_accession'])

	# Add Analysis
	notebook = AddAnalyses(notebook=notebook, toolkit_id=notebook_configuration['toolkit_id'])

	# Get string
	notebook_string = nbf.writes(notebook)

	# Return string
	return notebook_string