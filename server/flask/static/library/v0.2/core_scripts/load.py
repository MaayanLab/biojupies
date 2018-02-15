#################################################################
#################################################################
############### Load Dataset
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import pandas as pd
import urllib
import json
import gzip
import warnings
import os
with warnings.catch_warnings():
	warnings.simplefilter("ignore")
	import h5py

##### 2. Other libraries #####

#######################################################
#######################################################
########## S1. Dataset Loading
#######################################################
#######################################################

#############################################
########## 1. ARCHS4
#############################################

def archs4(gse, platform):

    # Load HDF5 File
    # h5 = '/Users/denis/Data/archs-v1.1/h5/{gse}-{platform}.h5'.format(**locals())
    h5 = '{gse}-{platform}.h5'.format(**locals())
    with open(h5, 'wb') as openfile:
        openfile.write(urllib.request.urlopen('https://storage.googleapis.com/archs4-packages/'+h5).read())
    f = h5py.File(h5, 'r')
    
    # Get data
    rawcount_dataframe = pd.DataFrame(data=f['data']['expression'].value, columns=[x for x in f['meta']['gene']['symbol'].value], index=[x for x in f['meta']['sample']['Sample_geo_accession'].value]).T
    sample_metadata_dataframe = pd.DataFrame({key: [x for x in value.value] for key, value in f['meta']['sample'].items()}).set_index('Sample_geo_accession').rename(columns={'Sample_title': 'Sample Title'})
    # for column in sample_metadata_dataframe.columns:
    # 	unique_vals = list(set(sample_metadata_dataframe[column]))
    # 	if len(unique_vals) == 1 or any([len(x) > 20 for x in unique_vals]):
	   #  	sample_metadata_dataframe.drop(column, axis=1, inplace=True)
    data = {'rawdata': rawcount_dataframe, 'sample_metadata': sample_metadata_dataframe, 'dataset_metadata': {'source': 'archs4', 'datatype': 'rnaseq'}}
    os.unlink(h5)
    
    # Return
    return data

#############################################
########## 2. H5
#############################################

def h5(path, data_type='rnaseq', from_url=False):

	# Read H5
	if from_url:
		pass
	else:
		f = h5py.File(path, "r")

	# Get expression
	expression_dataframe = pd.DataFrame(f['data']['expression'].value, index=f['meta']['genes'].value.astype(str), columns=f['meta']['samples'].value.astype(str))

	# Sample metadata
	sample_metadata_dataframe = pd.DataFrame({key: meta.value.astype(str) if meta.value.dtype == 'S9' else meta.value for key, meta in f['meta'].items() if key != 'genes'}).set_index('samples')

	# Fix bytes
	sample_metadata_dataframe.index = sample_metadata_dataframe.index.astype(str)
	for col in sample_metadata_dataframe.columns:
		if type(sample_metadata_dataframe[col].iloc[0]) == bytes:
			sample_metadata_dataframe[col] = [x.decode('utf-8') for x in sample_metadata_dataframe[col]]

	# Return
	return {'rawdata': expression_dataframe, 'sample_metadata': sample_metadata_dataframe, 'dataset_metadata': {'source': 'h5', 'data_type': data_type}}
