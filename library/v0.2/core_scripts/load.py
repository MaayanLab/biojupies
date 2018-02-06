#################################################################
#################################################################
############### Load Dataset
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import urllib
import json
import gzip
import h5py
import pandas as pd

##### 2. Other libraries #####

#######################################################
#######################################################
########## S1. Dataset Loading
#######################################################
#######################################################

#############################################
########## 1. ARCHS4
#############################################

def archs4(gse, platform=None):
 
	# Get Link Dict
	with urllib.request.urlopen("http://amp.pharm.mssm.edu/archs4/search/getGSEmatrix.php?gse={gse}".format(**locals())) as response:
		link_dict = {x['platform']: x['ziplink'] for x in json.loads(response.read())}

	# Get Link
	if platform:
		link = link_dict[platform]
	else:
		platform = list(link_dict.keys())[0]
		link = list(link_dict.values())[0]

	# Read Data
	response = urllib.request.urlopen(urllib.request.Request(link, headers={"Accept-Encoding": "gzip"}))
	data = gzip.decompress(response.read()).decode('utf-8')

	# Get Raw Counts
	rawcount_dataframe = pd.DataFrame([x.split('\t') for x in data.split('\n')[1:] if '!' not in x]).drop(0)
	rawcount_dataframe = rawcount_dataframe.rename(columns=rawcount_dataframe.iloc[0]).drop(1).set_index('ID_REF').fillna(0).astype('int')

	# Get Sample Metadata
	sample_metadata_dataframe = pd.DataFrame([x.split('\t') for x in data.split('\n')[1:] if any(y in x for y in ['!Sample_geo_accession', '!Sample_title', '!Sample_characteristics_ch1'])]).T
	sample_metadata_dataframe = sample_metadata_dataframe.rename(columns=sample_metadata_dataframe.iloc[0]).drop(0).set_index('!Sample_geo_accession').fillna(0)
	sample_metadata_dataframe['platform'] = platform

	# Return dict
	data = {'rawdata': rawcount_dataframe, 'sample_metadata': sample_metadata_dataframe, 'dataset_metadata': {'source': 'archs4', 'data_type': 'rnaseq'}}

	# Return
	return data

#############################################
########## 2. H5
#############################################

def h5(path, data_type, from_url=False):

	# Read H5
	if from_url:
		pass
	else:
		f = h5py.File(path, "r")

	# Get expression
	expression_dataframe = pd.DataFrame(f['data']['expression'].value, index=f['meta']['genes'].value.astype(str), columns=f['meta']['samples'].value.astype(str))

	# Sample metadata
	sample_metadata_dataframe = pd.DataFrame({key: meta.value.astype(str) if meta.value.dtype == 'S9' else meta.value for key, meta in f['meta'].items() if key != 'genes'}).set_index('samples')

	# Return
	return {'rawdata': expression_dataframe, 'sample_metadata': sample_metadata_dataframe, 'dataset_metadata': {'source': 'h5', 'data_type': data_type}}
