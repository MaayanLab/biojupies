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
import json, os
import pandas as pd
import numpy as np

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

	def upload_to_google(self, user_id):

		pass
	
	#############################################
	########## 4. Upload to Database
	#############################################

	def upload_to_database(self):

		pass
	