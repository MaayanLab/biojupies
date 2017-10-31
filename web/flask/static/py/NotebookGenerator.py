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

def GenerateNotebook(acc):

	# Create new notebook
	notebook = nbf.v4.new_notebook()

	# Load Libraries
	notebook['cells'].append(nbf.v4.new_code_cell('# Import Modules\nimport archs4'))

	# Fetch Data
	notebook['cells'].append(nbf.v4.new_code_cell('# Get Dataset\nrawcount_dataframe, sample_metadata_dataframe = archs4.fetch_dataset("{acc}")\nrawcount_dataframe.head()'.format(**locals())))
	notebook['cells'].append(nbf.v4.new_code_cell('# Show Metadata\nsample_metadata_dataframe'.format(**locals())))

	# Get string
	notebook_string = nbf.writes(notebook)

	# Return string
	return notebook_string