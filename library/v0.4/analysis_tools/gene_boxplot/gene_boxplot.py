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
import pandas as pd
import seaborn as sns

##### 2. Other libraries #####


#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(dataset, gene_symbol, groups):
	# Get normalized data
	logCPM_dataframe = np.log10(dataset['rawdata']/dataset['rawdata'].sum()*10**6+1)

	# Get group dataframe
	group_dataframe = pd.DataFrame([{'Group': group_label, 'sample': sample} for group_label, group_samples in groups.items() for sample in group_samples]).set_index('sample')

	# Get plot dataframe
	plot_dataframe = logCPM_dataframe.loc[gene_symbol].to_frame().merge(group_dataframe, left_index=True, right_index=True)
	return {'plot_dataframe': plot_dataframe, 'gene_symbol': gene_symbol}

#############################################
########## 2. Plot
#############################################

def plot(gene_boxplot_results):
	sns.boxplot(x='Group', y=gene_boxplot_results['gene_symbol'], data=gene_boxplot_results['plot_dataframe'])
	sns.despine()