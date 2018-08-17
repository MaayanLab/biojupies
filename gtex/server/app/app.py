#################################################################
#################################################################
############### Notebook Generator Website ######################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#######################################################
#######################################################
########## 1. App Configuration
#######################################################
#######################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. Flask modules #####
from flask import Flask, request
import os, h5py, json
import pandas as pd

#############################################
########## 2. App Setup
#############################################
##### 1. Flask App #####
# General
entry_point = '/biojupies-gtex'
app = Flask(__name__, static_url_path=os.path.join(entry_point, 'app/static'))

#######################################################
#######################################################
########## 2. Return Data
#######################################################
#######################################################
##### Handles GTEx data.

@app.route(entry_point, methods=['GET', 'POST'])
def index():

	# Read data from POST request
	if request.method == 'GET':
		samples = ["GTEX-14BIM-0011-R6b-SM-5S2VB", "GTEX-14JG1-0526-SM-6LLHW", "GTEX-1B97I-1526-SM-73KUK", "GTEX-16XZY-0426-SM-793BI", "GTEX-1CB4H-0126-SM-7IGN2"]
	elif request.method == 'POST':
		samples = list(set(request.json['samples']))

	# Read h5 file with data and metadata
	f = h5py.File('app/static/gtex_counts.h5', 'r')

	# Get sample indices
	sample_indices = [index for index, sample in enumerate(f['meta']['sample']['SAMPID']) if sample in samples]

	# Subset expression data based on sample IDs
	expression_subset = pd.DataFrame(f['data']['expression'][:, sample_indices], columns=samples, index=f['meta']['gene']['symbol']).rename_axis('gene_symbol')

	# Get metadata
	metadata_subset = pd.DataFrame({x: f['meta']['sample'][x][sample_indices] for x in f['meta']['sample'].keys()}).set_index('SAMPID')

	# Close file
	f.close()

	# Convert
	results = json.dumps({'rawdata': expression_subset.to_dict(), 'sample_metadata': metadata_subset.to_dict()})

	return results
