#######################################################
#######################################################
########## BioJupies Docker Utilities
#######################################################
#######################################################
##### Handles the download of BioJupies notebooks in the Docker container.
import os, urllib.request, urllib.parse, json

##################################################
########## 1. Download Notebook
##################################################

def download_notebook():

	# Check environmentas variable for notebook UID
	notebook_uid = os.environ.get('NOTEBOOK_UID')

	# If exists
	if notebook_uid:

		# Get Notebook Data URl
		notebook_data_url = 'http://amp.pharm.mssm.edu/biojupies/api/notebook/'+notebook_uid

		# Get Notebook Data
		with urllib.request.urlopen(notebook_data_url) as response:
			notebook_data = json.loads(response.read())
			
		# Get Notebook URL
		notebook_url = urllib.parse.quote(notebook_data['notebook_url'], safe=':/')
		print(notebook_url)

		# Get data
		os.system('wget '+notebook_url)

		# Jupyter Trust


##################################################
########## 2. Run Function
##################################################

download_notebook()