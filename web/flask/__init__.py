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
from flask import Flask, request, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

##### 2. Python modules #####
import os, sys, urllib.request, json, requests
from google.cloud import storage
from google.cloud.storage import Blob

##### 3. Custom modules #####
sys.path.append('static/py')
from NotebookGenerator import *
from NotebookManager import *
import KubernetesAPI

#############################################
########## 2. App Setup
#############################################
##### 1. Flask App #####
entry_point = '/notebook-generator-web'
app = Flask(__name__, static_url_path=os.path.join(entry_point, 'static'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##### 2. Database Connection #####
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
db = SQLAlchemy(app)

##### 3. API #####
NotebookManager = NotebookManager(db)

#######################################################
#######################################################
########## 2. Routes
#######################################################
#######################################################

#############################################
########## 1. Redirection
#############################################

@app.route(entry_point)
def index():

	# Return
	return render_template('index.html')

#############################################
########## 2. Dashboard
#############################################

@app.route(entry_point+'/dashboard')
def dashboard():

	# Launch User Deployment
	KubernetesAPI.LaunchDeployment(username='maayanlab')

	# Get Notebooks
	notebooks = NotebookManager.list_notebooks(user_id=1)

	# Return
	return render_template('dashboard.html', notebooks=notebooks)

#############################################
########## 3. Generate
#############################################

@app.route(entry_point+'/generate')
def generate():

	# Get Dataset Accession
	acc = request.args.get('acc')

	# Get Notebook String
	notebook_string = GenerateNotebook(acc)

	# Return
	return notebook_string

#############################################
########## 4. Launch
#############################################

@app.route(entry_point+'/launch', methods=['GET', 'POST'])
def launch():

	# Get accession
	accession = request.args.get('acc', 'GSE30017')

	# Get Notebook URL
	data = {
		'notebook_url': 'http://amp.pharm.mssm.edu/notebook-generator-web/generate?acc={accession}'.format(**locals()),
		'notebook_name': '{accession} Analysis Notebook.ipynb'.format(**locals()),
		'new_notebook': True
	}

	# Get Service IP
	service_ip = KubernetesAPI.LaunchDeployment(username='maayanlab')

	# Post Notebook to Pod Manager
	manager_url = 'http://{service_ip}:5000/notebook-generator-manager/download'.format(**locals())
	response = requests.post(manager_url, data=json.dumps(data))

	# Get Notebook URL
	live_notebook_url = response.text

	# Return
	return live_notebook_url

#############################################
########## 5. Upload
#############################################

@app.route(entry_point+'/upload', methods=['GET', 'POST'])
def upload():

	# Get POSTed data
	raw_notebook_url = json.loads(request.data)['raw_notebook_url']
	# raw_notebook_url = request.args.get('raw_notebook_url')

	# Upload to Google
	google_notebook_url = NotebookManager.upload_to_google(raw_notebook_url)

	# Add to database
	NotebookManager.upload_to_database(user_id=1, notebook_uid=os.path.basename(google_notebook_url))

	# Return
	return google_notebook_url

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