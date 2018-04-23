#################################################################
#################################################################
############### DE 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import numpy as np
import plotly.graph_objs as go
from plotly.offline import iplot
import pandas as pd

##### 2. Other libraries #####
from IPython.display import display, HTML


#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(signature_A, signature_B, signatures, fdr_threshold=0.05, logfc_threshold=1.5):

	# Get tables
	merged_dataframe = signatures[signature_A].rename(columns={'adj.P.Val': 'FDR'}).merge(signatures[signature_B].rename(columns={'adj.P.Val': 'FDR'}), left_index=True, right_index=True, suffixes=[signature_A, signature_B])

	# Loop through directions
	results = {}
	for direction in ['upregulated', 'downregulated']:
		subsets = {}
		for signature in [signature_A, signature_B]:
			subsets[signature] = (merged_dataframe['FDR'+signature] < fdr_threshold) & (merged_dataframe['logFC'+signature] > logfc_threshold if direction == 'upregulated' else merged_dataframe['logFC'+signature] < -logfc_threshold)
		tab = pd.crosstab(subsets[signature_A], subsets[signature_B])
		sets = [set(merged_dataframe[value].index) for value in subsets.values()]
		results[direction] = sets[0].intersection(sets[1])

	# Get results
	return results

#############################################
########## 2. Plot
#############################################

def plot(top_genes):
	return top_genes
