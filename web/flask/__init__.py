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
import os, sys, urllib.request, json, requests, re
from google.cloud import storage
from google.cloud.storage import Blob
import googleapiclient.discovery

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
########## 2. Static Pages
#######################################################
#######################################################

#############################################
########## 1. Redirection
#############################################

@app.route(entry_point)
def index():
	datasets = pd.read_table('static/data/archs4.txt')
	toolkits = pd.read_table('static/data/toolkits.txt')
	notebooks = NotebookManager.list_notebooks(user_id=1)
	# Return
	return render_template('index.html', datasets=datasets, toolkits=toolkits, notebooks=notebooks)

#######################################################
#######################################################
########## 3. Dashboard
#######################################################
#######################################################

#############################################
########## 1. Dashboard
#############################################

@app.route(entry_point+'/dashboard')
def dashboard():

	# Get Notebooks
	notebooks = NotebookManager.list_notebooks(user_id=1)

	# Return
	return render_template('dashboard.html', notebooks=notebooks)

#############################################
########## 2. Dashboard API
#############################################

@app.route(entry_point+'/api/dashboard', methods=['POST'])
def dashboard_api():

	# Launch User Deployment
	service_ip = KubernetesAPI.LaunchDeployment(username='maayanlab')

	# Return
	return service_ip

#######################################################
#######################################################
########## 4. Notebook Launching
#######################################################
#######################################################

#############################################
########## 1. Launch Notebook
#############################################

@app.route(entry_point+'/notebook/<notebook_uid>')
def notebook(notebook_uid):

	# Return
	return render_template('notebook.html', notebook_uid=notebook_uid)

#############################################
########## 2. Launch Notebook API
#############################################

@app.route(entry_point+'/api/notebook/<notebook_uid>', methods=['POST'])
def notebook_api(notebook_uid):

	# Get Service IP
	service_ip = KubernetesAPI.LaunchDeployment(username='maayanlab')

	# Get Bucket Contents
	bucket_contents = googleapiclient.discovery.build('storage', 'v1').objects().list(bucket='mssm-notebook-generator', fields='items(id,name,mediaLink)').execute()['items']

	# Get Raw Notebook URL
	raw_notebook_url = ''
	for content in bucket_contents:
		if content.get('id', '').split('/')[1] == notebook_uid and content.get('name', '') != notebook_uid+'/':
			raw_notebook_url = content['mediaLink']
			break

	# Get Notebook Name
	notebook_name = re.search('.*/{notebook_uid}/(.*.ipynb)'.format(**locals()), urllib.request.unquote(raw_notebook_url)).group(1)

	# Get Notebook Info
	notebook_info = json.dumps({'raw_notebook_url': raw_notebook_url, 'notebook_uid': notebook_uid, 'notebook_name': notebook_name})

	# Get Notebook URL
	live_notebook_url = requests.post('http://{service_ip}:5000/notebook-generator-manager/download'.format(**locals()), data=notebook_info).text

	# Return
	return live_notebook_url

#######################################################
#######################################################
########## 5. Notebook Handling
#######################################################
#######################################################

#############################################
########## 1. Generate API
#############################################

@app.route(entry_point+'/api/generate', methods=['POST'])
def generate_api():

	# Get data
	data = request.data.decode('utf-8')

	# Get Notebook String
	notebook_string = GenerateNotebook(data)

	# Get Notebook Data
	notebook_data = json.dumps({"notebook_name": '{data}.ipynb'.format(**locals()), "notebook_string": notebook_string})

	# Return
	return notebook_data

#############################################
########## 2. Upload API
#############################################

@app.route(entry_point+'/api/upload', methods=['POST'])
def upload_api():

	# Get POSTed data
	notebook_data = json.loads(request.data.decode('utf-8'))

	# Upload to Google
	notebook_uid = NotebookManager.upload_to_google(notebook_string=notebook_data['notebook_string'], notebook_name=notebook_data['notebook_name'])

	# Add to database
	NotebookManager.upload_to_database(user_id=1, notebook_uid=notebook_uid, notebook_name=notebook_data['notebook_name'])

	# Return
	return json.dumps({'notebook_uid': notebook_uid})

#############################################
########## 3. Delete API
#############################################

@app.route(entry_point+'/api/delete', methods=['POST'])
def delete_api():

	# Get POSTed data
	notebook_uid = request.data.decode('utf-8')

	# Delete from Google
	NotebookManager.delete_from_google(notebook_uid=notebook_uid)

	# Delete from database
	NotebookManager.delete_from_database(user_id=1, notebook_uid=notebook_uid)

	# Return
	return json.dumps({'notebook_uid': notebook_uid})

#############################################
########## 4. Display API
#############################################

@app.route(entry_point+'/api/download/<notebook_uid>', methods=['GET', 'POST'])
def download_api(notebook_uid):

	# Get Notebook URL
	notebook_url = NotebookManager.download_from_google(notebook_uid=notebook_uid)

	# Return
	return notebook_url

#############################################
########## 5. View API
#############################################

@app.route(entry_point+'/api/view/<notebook_uid>', methods=['GET', 'POST'])
def view_api(notebook_uid):

	# Return
	return redirect('http://nbviewer.jupyter.org/url/amp.pharm.mssm.edu/notebook-generator-web/api/download/{notebook_uid}'.format(**locals()))

#############################################
########## 3. New Notebook API
#############################################

# @app.route(entry_point+'/api/new_notebook', methods=['GET', 'POST'])
# def new_notebook_api():

# 	# Get accession
# 	accession = request.args.get('acc', 'GSE30017')

# 	# Get Notebook URL
# 	data = {
# 		'notebook_url': 'http://amp.pharm.mssm.edu/notebook-generator-web/generate?acc={accession}'.format(**locals()),
# 		'notebook_name': '{accession} Analysis Notebook.ipynb'.format(**locals()),
# 		'new_notebook': True
# 	}

# 	# Get Service IP
# 	service_ip = KubernetesAPI.LaunchDeployment(username='maayanlab')

# 	# Post Notebook to Pod Manager
# 	live_notebook_url = requests.post('http://{service_ip}:5000/notebook-generator-manager/download'.format(**locals()), data=json.dumps(data)).text

# 	# Return
# 	return live_notebook_url

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