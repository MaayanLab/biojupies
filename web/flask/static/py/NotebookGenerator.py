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

def GenerateNotebook(config):
	config = {'dataset': {'acc': config}}

	# Create new notebook
	notebook = nbf.v4.new_notebook()

	# Get Intro Text
	intro_text = """
# {acc} Analysis Notebook
## Overview
##### Introduction
This Notebook contains an analysis of GEO dataset [{acc}](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={acc}).  It has been programmatically generated with the Jupyter Notebook Generator, available at the following [link](https://amp.pharm.mssm.edu/notebook-generator-web/notebook?acc={acc}).

##### Sections
The report is divided in two sections:

1. *Data Processing*. This section covers the process of download and preprocessing of the dataset.
2. *Data Analysis*. This section covers the application of scripts and computational tools to analyze the dataset.

## 1. Data Processing
Here we download the dataset from the ARCHS4 library, load data and metadata in pandas DataFrames.
	""".format(**config['dataset'])

	# Load Libraries
	notebook['cells'].append(nbf.v4.new_markdown_cell(intro_text))
	notebook['cells'].append(nbf.v4.new_code_cell('# Import Modules\n%matplotlib inline\nimport sys\nsys.path.append("..")\nimport archs4\nimport pca\nimport heatmap\nimport clustergrammer\nfrom plotly.offline import init_notebook_mode\ninit_notebook_mode()'))

	# Fetch Data
	notebook['cells'].append(nbf.v4.new_code_cell('# Get Dataset\nrawcount_dataframe, sample_metadata_dataframe = archs4.fetch_dataset("{acc}")\nrawcount_dataframe.head()'.format(**config['dataset'])))
	notebook['cells'].append(nbf.v4.new_code_cell('# Show Metadata\nsample_metadata_dataframe'.format(**locals())))

	# # Add tools
	notebook['cells'].append(nbf.v4.new_markdown_cell('## 2. Data Analysis'))
	# notebook['cells'].append(nbf.v4.new_code_cell('# PCA\npca.display(rawcount_dataframe)'))
	# notebook['cells'].append(nbf.v4.new_markdown_cell(heatmap_analysis_text))
	# notebook['cells'].append(nbf.v4.new_code_cell('# Heatmap\nheatmap.display(rawcount_dataframe);'))
	# notebook['cells'].append(nbf.v4.new_markdown_cell(coexpression_analysis_text))
	# notebook['cells'].append(nbf.v4.new_code_cell('# Gene-gene Correlation Heatmap\nheatmap.display(rawcount_dataframe, correlation=True);'))
	# notebook['cells'].append(nbf.v4.new_code_cell('# Display Clustergrammer\nclustergrammer.display_clustergram(rawcount_dataframe)'))

	# Get string
	notebook_string = nbf.writes(notebook)

	# Return string
	return notebook_string