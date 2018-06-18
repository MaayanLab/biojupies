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
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'core_scripts', 'shared', 'shared.py'))
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
		'KEA_2015': '### A. KEA (experimentally validated targets)',
		'ARCHS4_Kinases_Coexp': '### B. ARCHS4 (coexpressed genes)'
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

def plot(enrichment_results, plot_counter):

	results_table(enrichment_results['enrichment_dataframe'].copy(), source_label='Kinase', target_label='substrate')

	# Figure Legend
	display(Markdown('** Table '+plot_counter('table')+' | Kinase Enrichment Analysis Results. **The figure contains browsable tables displaying the results of the Protein Kinase (PK) enrichment analysis generated using Enrichr. Every row represents a PK; significant PKs are highlighted in bold. A displays results generated using KEA, indicating PKs whose experimentally validated substrates are enriched. C displays results generated using the ARCHS4 library, indicating PKs whose top coexpressed genes (according to the ARCHS4 dataset) are enriched.'.format(**locals())))