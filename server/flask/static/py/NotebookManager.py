#################################################################
#################################################################
############### Notebook Manager API ############################
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
from google.cloud import storage
import random
import requests
import string
import os
import sys
import json
import urllib.parse
import nbformat as nbf
import pandas as pd
sys.path.append('static/py')
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import executenb

#############################################
########## 2. Variables
#############################################
##### 1. Notebook Execution #####
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

###
from nbconvert import HTMLExporter
from traitlets.config import Config
c = Config()
c.HTMLExporter.preprocessors = ['nbconvert.preprocessors.ExtractOutputPreprocessor']
html_exporter_with_figs = HTMLExporter(config=c)

#################################################################
#################################################################
############### 1. Functions ####################################
#################################################################
#################################################################

#############################################
########## 1. Execute Notebook
#############################################

def execute_notebook(notebook, execute=True, to_html=False):

	# Execute
	if execute:
		ep.preprocess(notebook, {'metadata': {'path': './static/library'}})

	if to_html:
		notebook = html_exporter_with_figs.from_notebook_node(notebook)[0]

	# Return
	return notebook

def execute_notebook_stream(notebook, execute=True, to_html=False):

	# Execute
	print('ExecutePreprocessor')
	print(ExecutePreprocessor)
	print(dir(ExecutePreprocessor))
	print(executenb)
	print(dir(executenb))
	if execute:
		notebook = executenb(notebook, cwd='./static/library')
		# ep.preprocess(notebook, {'metadata': {'path': './static/library'}})

	if to_html:
		notebook = html_exporter_with_figs.from_notebook_node(notebook)[0]

	# Return
	return notebook

#############################################
########## 2. Upload Notebook
#############################################

def upload_notebook(notebook, notebook_configuration, engine):

	# Get UID
	notebook_string = nbf.writes(notebook)
	notebook_uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))

	# Upload to Bucket
	client = storage.Client()
	bucket = client.get_bucket('jupyter-notebook-generator')
	blob = bucket.blob('{notebook_uid}/{notebook_configuration[notebook][title]}.ipynb'.format(**locals()))
	blob.upload_from_string(notebook_string, content_type='text/html')
	blob.make_public()
	notebook_url = urllib.parse.unquote(blob.public_url)

	# Upload to database
	notebook_dataframe = pd.Series({'notebook_uid': notebook_uid, 'notebook_url': notebook_url, 'notebook_configuration': json.dumps(notebook_configuration), 'version': notebook_configuration['notebook']['version'], 'gse': notebook_configuration['data']['parameters'].get('gse')}).to_frame().T
	print(notebook_dataframe)
	notebook_dataframe.to_sql('notebooks', engine, if_exists='append', index=False)

	# Return
	return notebook_url

#############################################
########## 3. Log Error
#############################################

def log_error(notebook_configuration, error, annotations, engine):

	# Get error type
	error_response = '<span> Sorry, there has been an error'
	if 'load_dataset' in error:
		error_type = 'load_dataset'
		error_response += ' loading the dataset.<br><br>Please try again with another one.'
	elif 'generate_signature' in error:
		error_type = 'generate_signature'
		error_response += ' generating the signature.<br><br>Please try again with different settings, or deselect the tools which require a signature.'
	elif 'normalize' in error:
		error_type = 'normalize'
		error_response += ' normalizing the dataset.<br><br>Please try again with different normalization method.'
	elif 'run' in error:
		tool_name = annotations['tools'][error.split("tool='")[-1].split("'")[0]]['tool_name']
		error_response += ' running {}.<br><br>Please try again by removing the selected tool.'.format(tool_name)
	else:
		error_type = 'unspecified'
		error_response = error_response.replace('error', 'unspecified error.')
		raise
	error_response += '<br><br>The error has been logged and we will work on fixing it.<br>&nbsp</span>'

	# Upload to database
	error_dataframe = pd.Series({'notebook_configuration': json.dumps(notebook_configuration), 'error': error, 'version': notebook_configuration['notebook']['version'], 'error_type': error_type, 'gse': notebook_configuration['data']['parameters'].get('gse')}).to_frame().T
	error_dataframe.to_sql('error_log', engine, if_exists='append', index=False)


	return error_response
