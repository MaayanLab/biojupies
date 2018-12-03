#######################################################
#######################################################
########## BioJupies Docker Utilities
#######################################################
#######################################################
##### Downloads all previous releases of BioJupies plug-in library to ensure reusability of all notebooks.
import requests, json, os

##################################################
########## 1. Download Notebook
##################################################

def download_libraries():

	# Get latest release
	r = requests.get('https://api.github.com/repos/MaayanLab/biojupies-plugins/releases')

	# Load in dictionary
	releases = json.loads(r.text)

	# Get releases
	tags = [x['tag_name'] for x in releases]

	# Loop through tags
	for tag in tags:
		command = '''
			wget https://api.github.com/repos/MaayanLab/biojupies-plugins/zipball/{tag};
			unzip {tag};
			rm {tag};
			mkdir {tag};
			mv $(find . -iname 'MaayanLab-biojupies-plugins-*')/library/* {tag};
			rm -r MaayanLab-biojupies-plugins-*; 
		'''.format(**locals())
		os.system(command)

##################################################
########## 2. Run Function
##################################################

download_libraries()