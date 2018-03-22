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
from IPython.display import display, HTML

#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(dataset, gene_symbols, groups):

	# Get normalized data
	logCPM_dataframe = np.log10(dataset['rawdata']/dataset['rawdata'].sum()*10**6+1)

	# Get group dataframe
	group_dataframe = pd.DataFrame([{'Group': group_label, 'sample': sample} for group_label, group_samples in groups.items() for sample in group_samples]).set_index('sample')

	# Get plot dataframe
	plot_dataframe = logCPM_dataframe.loc[gene_symbols].T.merge(group_dataframe, left_index=True, right_index=True)
	plot_dataframe = pd.melt(plot_dataframe, id_vars='Group', var_name='gene_symbol', value_name='logCPM')
	# display(HTML(plot_dataframe.groupby('Group').median().sort_values('logCPM', ascending=False).to_html()))
	return plot_dataframe

#############################################
########## 2. Plot
#############################################

def plot(plot_dataframe, order=None):
	sns.set_context('talk')
	g = sns.factorplot(x='Group', y='logCPM', col='gene_symbol', data=plot_dataframe, sharex=False, sharey=True, kind='box', col_wrap=3, order=order)
	g.set_axis_labels("", "logCPM").set_titles("{col_name}");