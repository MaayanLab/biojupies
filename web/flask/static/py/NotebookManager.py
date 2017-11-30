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
		self.Session = sessionmaker(bind=self.engine, autoflush=True)
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

	def upload_to_google(self, notebook_string, notebook_name):

		# Get string
		notebook_uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))

		#check UID, else create another

		# Upload to Google
		client = storage.Client()
		bucket = client.get_bucket('mssm-notebook-generator')
		blob = Blob(os.path.join(notebook_uid, notebook_name), bucket)
		# notebook_string = urllib.request.urlopen(raw_notebook_url).read().decode('utf-8')
		blob.upload_from_string(notebook_string)
		blob.make_public()

		return notebook_uid
		
	#############################################
	########## 4. Delete from Google
	#############################################

	def delete_from_google(self, notebook_uid):

		# Initialize session
		session = self.Session()

		# Get notebook name
		notebook_name = [x._asdict() for x in session.query(self.tables['notebook']).filter(self.tables['notebook'].columns['notebook_uid'] == notebook_uid).all()][0]['notebook_name']

		# Close session
		session.close()

		# Delete from Google
		client = storage.Client()
		bucket = client.get_bucket('mssm-notebook-generator')
		blob = Blob(os.path.join(notebook_uid, notebook_name), bucket)
		blob.delete()
			
	#############################################
	########## 5. Download from Google
	#############################################

	def download_from_google(self, notebook_uid):

		# Initialize session
		session = self.Session()

		# Get notebook name
		notebook_name = [x._asdict() for x in session.query(self.tables['notebook']).filter(self.tables['notebook'].columns['notebook_uid'] == notebook_uid).all()][0]['notebook_name']

		# Close session
		session.close()

		# Download from Google
		client = storage.Client()
		bucket = client.get_bucket('mssm-notebook-generator')
		blob = Blob(os.path.join(notebook_uid, notebook_name), bucket)
		notebook_string = blob.download_as_string().decode('utf-8')

		return notebook_string
	
	#############################################
	########## 6. Upload to Database
	#############################################

	def upload_to_database(self, user_id, notebook_uid, notebook_name):

		# Initialize session
		session = self.Session()

		# Insert
		session.execute(self.tables['notebook'].insert().values({'user_fk': user_id, 'notebook_uid': notebook_uid, 'notebook_name': notebook_name}))

		# Close session
		session.commit()
		session.close()
	
	#############################################
	########## 7. Delete from Database
	#############################################

	def delete_from_database(self, user_id, notebook_uid):

		# Initialize session
		session = self.Session()

		# Delete
		d = self.tables['notebook'].delete(self.tables['notebook'].columns['notebook_uid'] == notebook_uid)
		session.execute(d)

		# Close session
		session.commit()
		session.close()

