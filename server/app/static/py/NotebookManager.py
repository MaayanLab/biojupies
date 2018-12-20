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
import random
import string
import os
import json
import time
import nbformat as nbf
import pandas as pd
from google.cloud import storage
from flask_mail import Message

##### 2. Jupyter #####
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
from traitlets.config import Config

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

	# Convert to HTML
	if to_html:
		c = Config()
		c.HTMLExporter.preprocessors = ['nbconvert.preprocessors.ExtractOutputPreprocessor']
		html_exporter_with_figs = HTMLExporter(config=c)
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

	# Upload dataset
	dataset = notebook_configuration['data']['parameters'].get('gse') if notebook_configuration['data']['parameters'].get('gse') else notebook_configuration['data']['parameters'].get('uid')
	if not dataset:
		dataset = 'gtex'
	notebook_dataframe = pd.Series({'notebook_uid': notebook_uid, 'notebook_title': notebook_configuration['notebook']['title'], 'notebook_configuration': json.dumps(notebook_configuration), 'version': notebook_configuration['notebook']['version'], 'time': time, 'dataset': dataset, 'user_fk': user_id, 'private': 1 if user_id else 0}).to_frame().T
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

def log_error(notebook_configuration, error, annotations, session, tables, app, mail):

	# Generate new configuration
	new_configuration = notebook_configuration.copy()
	to_remove = []

	# Dataset loading
	if 'load_dataset' in error:
		error_type = 'load_dataset'
		error_title = 'Sorry, there has been an error loading the dataset.'
		error_subtitle = 'Please try again with another one.'
		retry_without_label = None
		new_configuration = None
		recommend = 'create-new'
		options = ['create-new', 'retry']

	# Signature generation
	elif 'generate_signature' in error:

		# New configuration
		new_configuration['signature'] = {}
		new_configuration['tools'] = [x for x in notebook_configuration['tools'] if annotations['tools'][x['tool_string']]['input'] == 'dataset']

		# Error message
		error_type = 'generate_signature'
		error_title = 'Sorry, there has been an error running differential gene expression.'
		error_subtitle = 'This is often caused when one or more samples have too many null or negative values, or when the uploaded dataset is not quantified as raw gene counts.'
		retry_without_label = 'Retry without differential gene expression'
		recommend = 'retry-without'
		options = ['create-new', 'retry', 'retry-without']

	# Plotly 
	elif 'PlotlyRequestError' in error:

		# Replace static with interactive in new configuration
		for tool_dict in new_configuration['tools']:
			if 'plot_type' in tool_dict.keys():
				tool_dict['plot_type'] == 'interactive'

		# Error message
		error_type = 'plotly_static'
		error_title = 'Sorry, there has been an error generating the static plots.'
		error_subtitle = 'This is usually caused when the static image generation server is experiencing heavy traffic, and is often resolved by trying again after a short time.'
		retry_without_label = 'Retry with interactive plots'
		new_configuration = new_configuration
		recommend = 'retry-without'
		options = ['create-new', 'retry', 'retry-without']

	# Tool
	elif 'run' in error:

		# Get tool metadata
		tool_string = error.split("tool='")[-1].split("'")[0]
		tool_name = annotations['tools'][tool_string]['tool_name']

		# Error subtitle
		if tool_string == 'pca':
			subtitle = 'This is often caused when one or more samples have too many null or negative values, or when the uploaded dataset is not quantified as raw gene counts.'
			recommend = 'retry-without'
			to_remove.append(tool_string)
		elif tool_string == 'clustergrammer':
			subtitle = 'This usually takes place when the Clustergrammer server is experiencing heavy traffic, and is often resolved by trying again after a short time.'
			recommend = 'retry'
			to_remove.append(tool_string)
		elif 'enrich' in tool_string:
			tool_name = 'enrichment analysis'
			subtitle = 'This usually takes place when the Enrichr server is experiencing heavy traffic, and is often resolved by trying again after a short time.'
			recommend = 'retry'
			to_remove = [tool_string for tool_string in annotations['tools'].keys() if 'enrich' in tool_string]
		else:
			subtitle = None
			to_remove.append(tool_string)
			recommend = 'retry-without'
		
		# Remove tool from configuration
		new_configuration['tools'] = [x for x in new_configuration['tools'] if x['tool_string'] not in to_remove]

		# Error message
		error_type = 'analysis_tool'
		error_title = 'Sorry, there has been an error running {}.'.format(tool_name)
		error_subtitle = subtitle
		retry_without_label = 'Retry without {}'.format(tool_name)
		recommend = 'retry-without'
		options: ['create-new', 'retry', 'retry-without'] if len(new_configuration['tools']) else ['create-new', 'retry']

	else:
		error_type = 'unspecified'
		error_title = 'Sorry, there has been an error generating the notebook.'
		error_subtitle = None
		retry_without_label = None
		new_configuration = None
		recommend = 'create-new'
		options = ['create-new', 'retry']

	# Upload
	error_id = session.execute(tables['error_log'].insert({'notebook_configuration': json.dumps(notebook_configuration), 'error': error, 'version': notebook_configuration['notebook']['version'], 'error_type': error_type, 'gse': notebook_configuration['data']['parameters'].get('gse')})).lastrowid
	session.commit()
	session.close()

	# Error message
	error_message = {
		'error_id': error_id,
		'error_type': error_type,
		'error_title': error_title,
		'error_subtitle': error_subtitle,
		'retry_without_label': retry_without_label,
		'new_configuration': new_configuration,
		'recommend': recommend,
		'options': options
	}
	print(error_message)

    # Send mail
	with app.app_context():
		msg = Message(subject='Notebook Generation Error #{}'.format(error_id),
						sender=os.environ['MAIL_USERNAME'],
						recipients=[os.environ['MAIL_RECIPIENT']],
                    body='https://amp.pharm.mssm.edu/biojupies/error/{error_id}\n\n{error}\n\n{notebook_configuration}\n\n{error_message}'.format(**locals()))
		mail.send(msg)

	return error_message
