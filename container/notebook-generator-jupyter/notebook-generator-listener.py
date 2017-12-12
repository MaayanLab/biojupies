#################################################################
#################################################################
############### Notebook Generator Listener #####################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#############################################
########## 1. Load libraries
#############################################
##### 1. Python modules #####
import time, logging, os, subprocess, requests, json
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

##### 2. Setup #####
# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Timeout
idle_buffer = 500
idle_timeout = time.time() + idle_buffer
max_timeout = time.time() + 1000

#######################################################
#######################################################
########## S1. Functions
#######################################################
#######################################################

#############################################
########## 1. Handler
#############################################

class MyHandler(PatternMatchingEventHandler):

	patterns = ["*.ipynb"]

	def refresh_timer(self):
		global idle_timeout
		idle_timeout = time.time() + idle_buffer

	def send_notebook(self, notebook_path):
		print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+' | Sending {notebook_path}...'.format(**locals()))
		basedir, notebook_uid, notebook_name = notebook_path.split('/')
		notebook_info = {'notebook_path': notebook_path, 'notebook_uid': notebook_uid}
		response = requests.post('http://amp.pharm.mssm.edu/notebook-generator-manager/update', data=json.dumps(notebook_info))
		print(response.text)

	def trust_notebook(self, notebook_path):
		output = subprocess.call(['jupyter', 'trust', notebook_path])

	def on_created(self, event):
		notebook_path = event.src_path
		print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+' | Created '+notebook_path)
		self.refresh_timer()
		self.trust_notebook(notebook_path)

	def on_modified(self, event):
		notebook_path = event.src_path
		print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+' | Modified '+notebook_path)
		self.refresh_timer()
		self.trust_notebook(notebook_path)
		self.send_notebook(notebook_path)

#############################################
########## 2. Stop Server
#############################################

def stopServer():

	# Print
	print('Stopping Server...')

	# Get URL
	url = 'http://amp.pharm.mssm.edu/notebook-generator-web/api/stop'
	response = requests.post(url)
	print(response.text)

#############################################
########## 3. Main
#############################################

def main():

	# Create observer
	observer = Observer()
	observer.schedule(MyHandler(), path='/notebook-generator', recursive=True)
	observer.start()

	# Start observing
	while time.time() < idle_timeout and time.time() < max_timeout:
		print('Deleting pod in at least '+str(round(idle_timeout-time.time()))+' seconds (maximum '+str(round(max_timeout-time.time()))+'s)...')
		time.sleep(60)

	# Stop observer
	observer.stop()
	observer.join()

	# Kill healthy directory
	stopServer()

##################################################
##################################################
########## Run Listener
##################################################
##################################################
main()