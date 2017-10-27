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
from flask import Flask, request, url_for

##### 2. Python modules #####
import os, sys, yaml

##### 3. Custom modules #####
sys.path.append('static/py')
from NotebookGenerator import *
from KubernetesAPI import *

#############################################
########## 2. App Setup
#############################################
##### 1. Flask App #####
entry_point = '/notebook-generator-web'
app = Flask(__name__, static_url_path=os.path.join(entry_point, 'static'))

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

	# Get Dataset Accession
	acc = request.args.get('acc', 'GSE00001')

	# Get Notebook URL
	notebook_url = url_for('generateNotebook', acc=acc, _external=True)
	notebook_url = 'http://amp.pharm.mssm.edu/notebook-generator-web/notebook?acc=GSE00001'

	# Generate Deployment
	GenerateDeployment(notebook_url)

	# Generate Service
	GenerateService()

	return notebook_url

#############################################
########## 2. Notebook Generation
#############################################

@app.route(entry_point+'/notebook')
def generateNotebook():

	# Get Dataset Accession
	acc = request.args.get('acc')

	# Get Notebook String
	notebook_string = GenerateNotebook(acc)

	# Return
	return notebook_string

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