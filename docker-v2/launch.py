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

		# Print status
		print("""
##############################
#### BioJupies Notebooks #####
##############################
You are running the BioJupies notebooks Docker image.

To access the Jupyter server, map container port 8888 using the -p flag (e.g. -p 8888:8888).
To download notebooks on your file system, mount a local volume to the /notebooks container path using the -v flag (e.g. -v /Users/user/Desktop:/notebooks).
For more information, please visit https://amp.pharm.mssm.edu/biojupies/docker.""")

		# Get notebook UID
		notebook_uid = input("\nTo continue, please provide the UID of the notebook you wish to download, then press enter. If you wish to view an example notebook, leave this blank.\n")

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
	
	# If no notebook selected
	else:

		# Check if notebook exists and/or directory is mounted
		try:
			if 'BioJupies Example Notebook | Normal vs Metastatic Melanoma.ipynb' not in os.listdir('/notebooks'):
				os.system('cd /notebooks; wget https://github.com/MaayanLab/biojupies/raw/master/docker/jupyter_notebooks/BioJupies%20Example%20Notebook%20%7C%20Normal%20vs%20Metastatic%20Melanoma.ipynb')
		except:
			pass


##################################################
########## 2. Run Function
##################################################

download_notebook()
