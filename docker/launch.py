#######################################################
#######################################################
########## BioJupies Docker Utilities
#######################################################
#######################################################
##### Handles the download of BioJupies notebooks in the Docker container.
import os, urllib.request, urllib.parse

##################################################
########## 1. Download Notebook
##################################################

def download_notebook():

	# Check environmentas variable for notebook UID
	notebook_uid = os.environ.get('NOTEBOOK_UID')
	print(notebook_uid)

	# If exists
	if notebook_uid:

		# # Get URL
		# notebook_url = 'http://localhost:5000/notebook-generator-website/api/notebook/'+notebook_uid

		# # Get Data
		# with urllib.request.urlopen(notebook_url) as response:
		# 	notebook_data = json.loads(response.read())
		notebook_url = urllib.parse.quote('https://storage.googleapis.com/jupyter-notebook-generator/4JetkKyEu/GSE75070 Analysis Notebook.ipynb', safe=':/')
			
		# Get data
		# os.system('wget {notebook_url}'.format(**notebook_data))
		os.system('wget '+notebook_url)

		# Jupyter Trust


##################################################
########## 2. Run Function
##################################################

download_notebook()