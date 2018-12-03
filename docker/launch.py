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

def download_notebook(notebook_uid = os.environ.get('NOTEBOOK_UID')):

	# Read UID
	if not notebook_uid:

		# Get notebook UID
		notebook_uid = input("\nPlease provide the UID of the notebook you wish to download, then press enter. If you wish to launch the Jupyter server without downloading a notebook, leave this blank.\n")

	# If exists
	if notebook_uid:

		# Get Notebook Data URl
		notebook_data_url = 'http://amp.pharm.mssm.edu/biojupies/api/notebook/'+notebook_uid

		# Get Notebook Data
		with urllib.request.urlopen(notebook_data_url) as response:
			notebook_data = json.loads(response.read())
			
		# Get Notebook URL
		try:
			notebook_url = urllib.parse.quote('https://storage.googleapis.com/jupyter-notebook-generator/{notebook_uid}/{notebook_title}.ipynb'.format(**notebook_data), safe=':/')
		except:
			raise ValueError('Sorry, the notebook could not be found.')

		# Get data
		os.system('wget '+notebook_url)

		# Jupyter Trust
		print('jupyter trust {}.ipynb'.format(notebook_data['notebook_title'].replace(' ', '\ ')))


##################################################
########## 2. Run Function
##################################################

download_notebook()
