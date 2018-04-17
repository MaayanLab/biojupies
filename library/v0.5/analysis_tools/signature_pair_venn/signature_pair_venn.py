#################################################################
#################################################################
############### DE 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import matplotlib.pyplot as plt
import scipy.stats as ss
import pandas as pd
from matplotlib_venn import venn2

##### 2. Other libraries #####


#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(signature_A, signature_B, signatures, col='logFC', logfc_threshold=1.5, fdr_threshold=0.05):

	# Get tables
	merged_dataframe = signatures[signature_A].rename(columns={'adj.P.Val': 'FDR'}).merge(signatures[signature_B].rename(columns={'adj.P.Val': 'FDR'}), left_index=True, right_index=True, suffixes=[signature_A, signature_B])

	# Loop through directions
	results = {}
	for direction in ['upregulated', 'downregulated']:
		subsets = {}
		for signature in [signature_A, signature_B]:
			subsets[signature] = (merged_dataframe['FDR'+signature] < fdr_threshold) & (merged_dataframe['logFC'+signature] > logfc_threshold if direction == 'upregulated' else merged_dataframe['logFC'+signature] < -logfc_threshold)
		tab = pd.crosstab(subsets[signature_A], subsets[signature_B])
		results[direction] = {'tab': tab, 'fet': ss.fisher_exact(tab), 'sets': {key: set(merged_dataframe[value].index) for key, value in subsets.items()}}

	return results

#############################################
########## 2. Plot
#############################################

def plot(venn_results, plot_counter):
	# Plot Venn
	for direction, results in venn_results.items():
		a = [x for x in results['sets'].values()]
		venn2(results['sets'].values(), set_labels=results['sets'].keys())
		plt.title(direction.title()+' Genes\np-value = '+'{:.2e}'.format(results['fet'][-1]))
		plt.show()