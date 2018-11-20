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
import time
import urllib.parse
import nbformat as nbf
import pandas as pd
from flask_mail import Message
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
sys.path.append('app/static/py')
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import executenb

#############################################
########## 2. Variables
#############################################
##### 1. Notebook Execution #####
# ep = ExecutePreprocessor(timeout=600)

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

def execute_notebook(notebook, execute=True, to_html=False, kernel_name='venv'):

	# Get start time
	start_time = time.time()

	# Initialize preprocess
	ep = ExecutePreprocessor(timeout=600, kernel_name=kernel_name)

	# Execute
	if execute:
		ep.preprocess(notebook, {'metadata': {'path': 'app/static/library'}})

	if to_html:
		notebook = html_exporter_with_figs.from_notebook_node(notebook)[0]

	# Return
	return notebook, round(time.time() - start_time)

#############################################
########## 2. Upload Notebook
#############################################

def upload_notebook(notebook, notebook_configuration, time, engine, user_id=None):

	# Get UID
	notebook_string = nbf.writes(notebook)
	notebook_uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))

	# Upload to Bucket
	client = storage.Client()
	bucket = client.get_bucket('jupyter-notebook-generator')
	blob = bucket.blob('{notebook_uid}/{notebook_configuration[notebook][title]}.ipynb'.format(**locals()))
	blob.upload_from_string(notebook_string, content_type='text/html')
	blob.make_public()
	# notebook_url = urllib.parse.unquote(blob.public_url)

	# Upload to database
	# notebook_dataframe = pd.Series({'notebook_uid': notebook_uid, 'notebook_url': notebook_url, 'notebook_configuration': json.dumps(notebook_configuration), 'version': notebook_configuration['notebook']['version'], 'gse': notebook_configuration['data']['parameters'].get('gse')}).to_frame().T
	# notebook_dataframe.to_sql('notebooks', engine, if_exists='append', index=False)

	### New Upload
	# Upload dataset
	dataset = notebook_configuration['data']['parameters'].get('gse') if notebook_configuration['data']['parameters'].get('gse') else notebook_configuration['data']['parameters'].get('uid')
	if not dataset:
		dataset = 'gtex'
	notebook_dataframe = pd.Series({'notebook_uid': notebook_uid, 'notebook_title': notebook_configuration['notebook']['title'], 'notebook_configuration': json.dumps(notebook_configuration), 'version': notebook_configuration['notebook']['version'], 'time': time, 'dataset': dataset, 'user_fk': user_id, 'private': 1 if user_id else 0}).to_frame().T
	print(notebook_dataframe)
	notebook_dataframe.to_sql('notebook', engine, if_exists='append', index=False)

	# Get tool IDs
	tool_dict = pd.read_sql_table('tool', engine).set_index('tool_string')['id'].to_dict()

	# Get notebook ID
	notebook_id = pd.read_sql_query('SELECT id FROM notebook WHERE notebook_uid = "{}"'.format(notebook_uid), engine)['id'][0]

	# Notebook-tool dataframe
	notebook_tool_dataframe = pd.DataFrame({'tool_fk': [tool_dict[x['tool_string']] for x in notebook_configuration['tools']], 'notebook_fk': notebook_id})
	notebook_tool_dataframe.to_sql('notebook_tool', engine, if_exists='append', index=False)

	# Notebook-tag dataframe
	if notebook_configuration.get('terms'):
		notebook_tag_dataframe = pd.DataFrame({'ontology_term_fk': [x for x in notebook_configuration.get('terms')], 'notebook_fk': notebook_id})
		notebook_tag_dataframe.to_sql('notebook_ontology_term', engine, if_exists='append', index=False)

	# Return
	return notebook_uid

#############################################
########## 3. Log Error
#############################################

def log_error(notebook_configuration, error, annotations, engine, app, mail):

	# Get error type
	error_response = '<span> Sorry, there has been an error'
	if 'load_dataset' in error:
		error_type = 'load_dataset'
		error_response += ' loading the dataset.<br><br>Please try again with another one.'
	elif 'generate_signature' in error:
		error_type = 'generate_signature'
		error_response += ' generating the signature.<br><br>This is often caused by one or more samples having too many null values, or when the uploaded dataset is not quantified as raw gene counts.<br><br>Please try again with different groups, or remove the tools which require a signature.'
	elif 'run' in error:
		tool_name = annotations['tools'][error.split("tool='")[-1].split("'")[0]]['tool_name']
		error_type = tool_name
		response = ' running {}.<br><br>Please try again by removing the selected tool.'.format(tool_name)
		if tool_name == 'PCA':
			response.replace('<br><br>', '<br><br>This is often caused by one or more samples having too many null values, or when the uploaded dataset is not quantified as raw gene counts.<br><br>')
		elif 'L1000CDS2' in tool_name:
			response.replace('<br><br>', '<br><br>This is likely due to the fact that the tool was unable to identify gene symbols in the dataset.<br><br>')
		error_response += response
	else:
		error_type = 'unspecified'
		# error_response = error_response.replace('error', 'unspecified error.')

	# Prepare session
	Session = sessionmaker(bind=engine)
	metadata = MetaData()
	metadata.reflect(bind=engine)
	tables = metadata.tables

	# Upload
	session = Session()
	error_id = session.execute(tables['error_log'].insert({'notebook_configuration': json.dumps(notebook_configuration), 'error': error, 'version': notebook_configuration['notebook']['version'], 'error_type': error_type, 'gse': notebook_configuration['data']['parameters'].get('gse')})).lastrowid
	session.commit()
	session.close()

    # Send mail
	with app.app_context():
		msg = Message(subject='Notebook Generation Error #{}'.format(error_id),
						sender=os.environ['MAIL_USERNAME'],
						recipients=[os.environ['MAIL_RECIPIENT']],
                    body='https://amp.pharm.mssm.edu/biojupies/error/{error_id}'.format(**locals()))
		mail.send(msg)

	return error_id, error_response
