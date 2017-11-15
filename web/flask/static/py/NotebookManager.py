#################################################################
#################################################################
############### Notebook Generator API ##########################
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
import json, os, random, string, urllib.request
import pandas as pd
import numpy as np
from google.cloud import storage
from google.cloud.storage import Blob

##### 2. Database modules #####
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

#################################################################
#################################################################
############### 1. Notebook Manager #############################
#################################################################
#################################################################

#############################################
########## 1. Initialization
#############################################

class NotebookManager:

	def __init__(self, db):
		
		# Save engine and tables
		self.engine = db.engine
		self.Session = sessionmaker(bind=self.engine)
		metadata = MetaData()
		metadata.reflect(bind=self.engine)
		self.tables = metadata.tables

	#############################################
	########## 2. Get Notebooks
	#############################################

	def list_notebooks(self, user_id):

		# Initialize session
		session = self.Session()

		# Get Notebooks
		notebooks = [x._asdict() for x in session.query(self.tables['notebook']).filter(self.tables['notebook'].columns['user_fk'] == user_id).all()]

		# Close session
		session.close()

		return notebooks
	
	#############################################
	########## 3. Upload to Google
	#############################################

	def upload_to_google(self, raw_notebook_url):

		# Get string
		notebook_uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))

		#check UID, else create another

		# Upload to Google
		client = storage.Client()
		bucket = client.get_bucket('mssm-notebook-generator')
		blob = Blob(os.path.join(notebook_uid, os.path.basename(raw_notebook_url)), bucket)
		notebook_string = urllib.request.urlopen(raw_notebook_url).read().decode('utf-8')
		blob.upload_from_string(notebook_string)
		blob.make_public()

		return notebook_uid
	
	#############################################
	########## 4. Upload to Database
	#############################################

	def upload_to_database(self, user_id, notebook_uid):

		# Initialize session
		session = self.Session()

		# Insert
		session.execute(self.tables['notebook'].insert().values({'user_fk': 1, 'notebook_uid': notebook_uid}))

		# Close session
		session.commit()
		session.close()

