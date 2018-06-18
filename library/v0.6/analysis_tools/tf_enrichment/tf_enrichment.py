#################################################################
#################################################################
############### DE 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import qgrid, requests, json, sys, os
import pandas as pd
import numpy as np
from IPython.display import display, Markdown, HTML

##### 2. Other libraries #####
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'core_scripts', 'shared'))
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
		'ChEA_2016': '### A. ChEA (experimentally validated targets)',
		'ENCODE_TF_ChIP-seq_2015': '### B. ENCODE (experimentally validated targets)',
		'ARCHS4_TFs_Coexp': '### C. ARCHS4 (coexpressed genes)'
	}

	# Initialize results
	results = []

	# Loop through genesets
	for geneset in ['upregulated', 'downregulated']:

		# Append ChEA results
		enrichment_dataframe = get_enrichr_results(enrichr_results[geneset]['userListId'], gene_set_libraries=libraries)
		enrichment_dataframe['geneset'] = geneset
		results.append(enrichment_dataframe)

	# Concatenate results
	enrichment_dataframe = pd.concat(results)

	return {'enrichment_dataframe': enrichment_dataframe, 'signature_label': signature_label}

#############################################
########## 2. Plot
#############################################

def plot(tf_analysis_results, plot_counter):

	results_table(tf_analysis_results['enrichment_dataframe'].copy(), source_label='Transcription Factor', target_label='target')

	# Figure Legend
	display(Markdown('** Table '+plot_counter('table')+' | Transcription Factor Enrichment Analysis Results. **The figure contains scrollable tables displaying the results of the Transcription Factor (TF) enrichment analysis generated using Enrichr. Every row represents a TF; significant TFs are highlighted in bold. A and B display results generated using ChEA and ENCODE libraries, indicating TFs whose experimentally validated targets are enriched. C displays results generated using the ARCHS4 library, indicating TFs whose top coexpressed genes (according to the ARCHS4 dataset) are enriched.'.format(**locals())))