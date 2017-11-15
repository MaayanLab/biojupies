#################################################################
#################################################################
############### Datasets2Tools Website Backend ##################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#######################################################
#######################################################
########## 1. App Configuration
#######################################################
#######################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. Flask modules #####
from flask import Flask, request, url_for, send_from_directory

##### 2. Python modules #####
import os, sys, json, nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import urllib.request

##### 3. Custom modules #####
sys.path.append('static/py')
from SendNotebook import *

#############################################
########## 2. App Setup
#############################################
##### 1. Flask App #####
entry_point = '/notebook-generator-manager'
app = Flask(__name__, static_url_path=os.path.join(entry_point, 'static'))

#######################################################
#######################################################
########## 2. Routes
#######################################################
#######################################################

#############################################
########## 1. Homepage
#############################################

@app.route(entry_point)
def index():
	return 'Welcome {username}'.format(**os.environ)

#############################################
########## 2. Download
#############################################

@app.route(entry_point+'/download', methods=['POST'])
def download():

	# Get POSTed Data
	data = json.loads(request.data)

	# Get file
	notebook_file = os.path.join('notebooks', data['notebook_name'])

	# Save Notebook to File
	if not os.path.exists(notebook_file):
		urllib.request.urlretrieve(data['notebook_url'], notebook_file)

	# Get Notebook URLs
	raw_notebook_url = os.path.join(request.host_url, 'notebook-generator-manager', 'notebooks', data['notebook_name'])
	live_notebook_url = os.path.join(request.host_url.replace('5000', '8888'), 'notebooks', 'notebooks', data['notebook_name'])

	# Upload to Google
	if data['new_notebook']:
		google_notebook_url = SendNotebook(raw_notebook_url)
	else:
		google_notebook_url = data['google_notebook_url']

	# Return
	urls = {'raw_notebook_url': raw_notebook_url, 'live_notebook_url': live_notebook_url, 'google_notebook_url': google_notebook_url}
	return json.dumps(urls)

#############################################
########## 3. Send
#############################################

@app.route(entry_point+'/send', methods=['POST'])
def send():

	# Get POSTed Data
	raw_notebook_url = json.loads(request.data['raw_notebook_url'])

	# Send
	google_notebook_url = SendNotebook(raw_notebook_url)

	# Return
	return google_notebook_url

#############################################
########## 4. Notebooks
#############################################

@app.route(entry_point+'/notebooks/<path:path>')
def notebooks(path):

	# Return
	return send_from_directory('notebooks', path)

#######################################################
#######################################################
########## 3. Run App
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')