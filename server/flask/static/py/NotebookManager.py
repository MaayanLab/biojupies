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
import urllib.parse
from nbconvert.preprocessors import ExecutePreprocessor
import nbformat as nbf

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

#############################################
########## 2. Upload Notebook
#############################################

def upload_notebook(notebook, notebook_title):

	# Get UID
	notebook_string = nbf.writes(notebook)
	notebook_uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))

	# Upload to Bucket
	client = storage.Client()
	bucket = client.get_bucket('jupyter-notebook-generator')
	blob = bucket.blob('{notebook_uid}/{notebook_title}.ipynb'.format(**locals()))
	blob.upload_from_string(notebook_string, content_type='text/html')
	blob.make_public()

	# Return
	return urllib.parse.unquote(blob.public_url)
