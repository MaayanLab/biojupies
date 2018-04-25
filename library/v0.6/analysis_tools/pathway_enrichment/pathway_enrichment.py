#################################################################
#################################################################
############### Enrichment Analysis
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import pandas as pd
import os
import sys
from IPython.display import display, Markdown

##### 2. Other libraries #####
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
	os.path.realpath(__file__)))), 'core_scripts', 'shared', 'shared.py'))
from shared import *

#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(enrichr_results, signature_label):

	# Libraries
	libraries = {
		'KEGG_2016': 'KEGG Pathways',
		'WikiPathways_2016': 'WikiPathways',
		'Reactome_2016': 'Reactome Pathways'
	}

	# Get Enrichment Results
	enrichment_results = {geneset: get_enrichr_results(enrichr_results[geneset]['userListId'], gene_set_libraries=libraries) for geneset in ['upregulated', 'downregulated']}
	enrichment_results['signature_label'] = signature_label

	# Return
	return enrichment_results

#############################################
########## 2. Plot
#############################################

def plot(enrichment_results, plot_counter):

	# Create dataframe
	enrichment_dataframe = pd.concat([enrichment_results['upregulated'], enrichment_results['downregulated']])

	# Plot barcharts
	for gene_set_library in enrichment_dataframe['gene_set_library'].unique():
		plot_library_barchart(enrichment_results, gene_set_library, enrichment_results['signature_label'], 10, 300)

	# Figure legend
	display(Markdown('** Figure '+plot_counter()+' | Pathway Enrichment Analysis Results.** The figure contains interactive bar charts displaying the results of the pathway enrichment analysis generated using Enrichr. The x axis indicates the enrichment score for each term. Significant terms are highlighted in bold. Additional information about enrichment results is available by hovering over each bar.'.format(**locals())))