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

def run(signature_A, signature_B, signatures, col='logFC'):

	# Merge signatures
	dataframes = []
	for signature in [signature_A, signature_B]:
		signature_dataframe = signatures[signature]
		signature_dataframe['signature'] = signature
		dataframes.append(signature_dataframe)
	merged_dataframe = pd.concat(dataframes)

	# Add logP
	merged_dataframe['logP'] = -np.log10(merged_dataframe['adj.P.Val'])

	# Get significant genes in both signatures
	significant_genes = (merged_dataframe.reset_index().pivot_table(index='gene_symbol', columns='signature', values='adj.P.Val') < 0.05).replace(False, np.nan).dropna().index
	up_genes = (abs(merged_dataframe.reset_index().pivot_table(index='gene_symbol', columns='signature', values='logFC')) > 1.5).replace(False, np.nan).dropna().index
	dn_genes = (abs(merged_dataframe.reset_index().pivot_table(index='gene_symbol', columns='signature', values='logFC')) < -1.5).replace(False, np.nan).dropna().index

	# Get gene sets
	top_genes = set(significant_genes).intersection(set(up_genes))
	bottom_genes = set(significant_genes).intersection(set(dn_genes))
	# top_genes = merged_dataframe.loc[significant_genes].reset_index().groupby('gene_symbol')['logP'].sum().rename('logP').sort_values(ascending=False).to_frame().index[:15]

	# display(HTML(merged_dataframe.loc[top_genes].to_html()))

	# Get results
	return {'upregulated': top_genes, 'downregulated': bottom_genes}

#############################################
########## 2. Plot
#############################################

def plot(top_genes):
	return top_genes
