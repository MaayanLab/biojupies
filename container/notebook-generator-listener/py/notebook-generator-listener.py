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
import time, logging, os
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

##### 2. Setup #####
# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Timeout
seconds = 5
timeout = time.time() + seconds

#######################################################
#######################################################
########## S1. Functions
#######################################################
#######################################################

#############################################
########## 1. Handler
#############################################

class MyHandler(PatternMatchingEventHandler):

	patterns = ["*.txt"]

	def refresh_timer(self):
		global timeout
		timeout = time.time() + seconds

	def upload_file(self, event):
		file = event.src_path
		print('Uploading {file}...'.format(**locals()))
		pass

	def process(self, event):
		self.refresh_timer()
		self.upload_file(event)

	def on_created(self, event):
		self.process(event)

#############################################
########## 2. Main
#############################################

def main():

	# Create observer
	observer = Observer()
	observer.schedule(MyHandler(), path='.')
	observer.start()

	# Start observing
	while time.time() < timeout:
		print(round(timeout-time.time()))
		time.sleep(1)

	# Stop observer
	observer.stop()
	observer.join()

	# Kill healthy directory
	healthy_dir = '/healthy'
	if os.path.exists(healthy_dir):
		pass

##################################################
##################################################
########## Run Listener
##################################################
##################################################
main()