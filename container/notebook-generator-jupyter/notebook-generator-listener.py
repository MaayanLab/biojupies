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
import time, logging, os, subprocess
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

	def upload_notebook(self, notebook_path):
		pass

	def trust_notebook(self, notebook_path):
		output = subprocess.call(['jupyter', 'trust', notebook_path])

	def on_created(self, event):
		notebook_path = event.src_path
		print('Created '+notebook_path)
		self.refresh_timer()
		self.trust_notebook(notebook_path)
		# self.upload_notebook(notebook_path)

	def on_modified(self, event):
		notebook_path = event.src_path
		print('Modified '+notebook_path)
		self.refresh_timer()
		self.trust_notebook(notebook_path)
		# self.upload_notebook(notebook_path)

#############################################
########## 2. Main
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
	os.unlink('/notebook-generator/healthy')

##################################################
##################################################
########## Run Listener
##################################################
##################################################
main()