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

#############################################
########## 2. Variables
#############################################
##### 1. Helper Function #####


#################################################################
#################################################################
############### 1. Functions ####################################
#################################################################
#################################################################

#############################################
########## 1. Upload Notebook
#############################################

def upload_notebook(notebook_html):

	# Get UID
	notebook_uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))

	# Upload to Bucket
	client = storage.Client()
	bucket = client.get_bucket('jupyter-notebook-generator')
	blob = bucket.blob(notebook_uid+'/notebook.html')
	blob.upload_from_string(notebook_html, content_type='text/html')
	blob.make_public()

	# Return
	return urllib.parse.unquote(blob.public_url)


#############################################
########## 2. Launch Notebook
#############################################

def launch_notebook(notebook_html, notebook_title, username):

	# PUT
	# r = requests.put('http://localhost:8888/api/contents', data={'content': notebook_json, 'name': notebook_title, 'path': '/', 'type': 'notebook', 'format': 'json'})
	# upload to google cloud storage
	# get username server with notebook title

	return 'url'

