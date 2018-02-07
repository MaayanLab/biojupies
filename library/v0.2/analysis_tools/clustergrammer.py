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

def run(dataset, nr_genes=500):
	net = Network(clustergrammer_widget)
	data = np.log10(dataset['rawdata']/dataset['rawdata'].sum()+1)
	net.load_df(data)
	net.add_cats(cat_data=[{'title': index, 'cats': {str(value): rowData[rowData==value].index.tolist() for value in set(rowData.values)}} for index, rowData in dataset['sample_metadata'].T.iterrows()], axis='col')
	net.filter_N_top('row', 500, 'var')
	net.normalize(axis='row', norm_type='zscore', keep_orig=True)
	net.cluster()
	return net

#############################################
########## 2. Plot
#############################################

def plot(net):
	return net.widget()
