#################################################################
#################################################################
############### Clustergrammer 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
from clustergrammer_widget import *
import numpy as np

##### 2. Other libraries #####

#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(dataset, normalization='rawdata', normalize_cols=False, log=False, z_score=False, nr_genes=1500):
	net = Network(clustergrammer_widget)
	data = dataset[normalization]
	if normalize_cols:
		data = data/data.sum()
	if log:
		data = np.log10(data+1)
	net.load_df(data)
	net.add_cats(cat_data=[{'title': index, 'cats': {str(value): rowData[rowData==value].index.tolist() for value in set(rowData.values)}} for index, rowData in dataset['sample_metadata'].T.iterrows()], axis='col')
	net.filter_N_top('row', nr_genes, 'var')
	if z_score:
		net.normalize(axis='row', norm_type='zscore', keep_orig=True)
	net.cluster()
	return net

#############################################
########## 2. Plot
#############################################

def plot(net):
	return net.widget()
