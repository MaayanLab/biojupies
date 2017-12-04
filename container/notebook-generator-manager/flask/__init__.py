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

	# Get Notebook Data
	notebook_info = json.loads(request.data)

	# Get file
	notebook_file_path = os.path.join('notebooks', notebook_info['notebook_uid'], notebook_info['notebook_name'])

	# Save Notebook to File
	if not os.path.exists(notebook_file_path):
		os.makedirs(os.path.dirname(notebook_file_path))
		urllib.request.urlretrieve(notebook_info['raw_notebook_url'], notebook_file_path)

	# Get Notebook URLs
	live_notebook_url = os.path.join(request.host_url.replace('5000', '8888'), 'notebooks', 'notebooks', notebook_info['notebook_uid'], notebook_info['notebook_name'])

	return live_notebook_url

#############################################
########## 3. Send
#############################################

# @app.route(entry_point+'/send', methods=['POST'])
# def send():

# 	# Get POSTed Data
# 	raw_notebook_url = request.data

# 	# Send
# 	google_notebook_url = SendNotebook(raw_notebook_url)

# 	# Return
# 	return google_notebook_url

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