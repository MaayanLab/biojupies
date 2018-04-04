#################################################################
#################################################################
############### DE 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import qgrid, requests, json
import pandas as pd
import numpy as np
from IPython.display import display, Markdown, HTML

##### 2. Other libraries #####

#######################################################
#######################################################
########## Support
#######################################################
#######################################################

#############################################
########## 1. Get Enrichr Results
#############################################

def get_enrichr_results(user_list_id, gene_set_libraries, overlappingGenes=True):
	ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/enrich'
	query_string = '?userListId=%s&backgroundType=%s'
	results = []
	for gene_set_library in gene_set_libraries:
		response = requests.get(
			ENRICHR_URL + query_string % (user_list_id, gene_set_library)
		 )
		if not response.ok:
			raise Exception('Error fetching enrichment results')

		data = json.loads(response.text)
		resultDataframe = pd.DataFrame(data[gene_set_library], columns=['rank', 'term_name', 'pvalue', 'zscore', 'combined_score', 'overlapping_genes', 'FDR', 'old_pvalue', 'old_FDR'])
		selectedColumns = ['term_name','zscore','combined_score','pvalue', 'FDR'] if not overlappingGenes else ['term_name','zscore','combined_score','FDR', 'pvalue', 'overlapping_genes']
		resultDataframe = resultDataframe.loc[:,selectedColumns]
		resultDataframe['gene_set_library'] = gene_set_library
		results.append(resultDataframe)
	concatenatedDataframe = pd.concat(results)
	return concatenatedDataframe

#############################################
########## 2. Display Result Table
#############################################

def results_table(enrichment_dataframe, source_label, target_label):

	# Get libraries
	for gene_set_library in enrichment_dataframe['gene_set_library'].unique():

		# Get subset
		enrichment_dataframe_subset = enrichment_dataframe[enrichment_dataframe['gene_set_library'] == gene_set_library].copy()

		# Get unique values from source column
		enrichment_dataframe_subset[source_label] = [x.split('_')[0] for x in enrichment_dataframe_subset['term_name']]
		enrichment_dataframe_subset = enrichment_dataframe_subset.sort_values(['FDR', 'pvalue']).rename(columns={'pvalue': 'P-value'}).drop_duplicates(source_label)

		# Add links and bold for significant results
		enrichment_dataframe_subset[source_label] = ['<a href="http://www.mirbase.org/cgi-bin/query.pl?terms={x}" target="_blank">{x}</a>'.format(**locals()) for x in enrichment_dataframe_subset[source_label]]
		enrichment_dataframe_subset[source_label] = [rowData[source_label].replace('target="_blank">', 'target="_blank"><b>').replace('</a>', '*</b></a>') if rowData['FDR'] < 0.05 else rowData[source_label] for index, rowData in enrichment_dataframe_subset.iterrows()]

		# Add rank
		enrichment_dataframe_subset['Rank'] = ['<b>'+str(x+1)+'</b>' for x in range(len(enrichment_dataframe_subset.index))]

		# Add overlapping genes with tooltip
		enrichment_dataframe_subset['nr_overlapping_genes'] = [len(x) for x in enrichment_dataframe_subset['overlapping_genes']]
		enrichment_dataframe_subset['overlapping_genes'] = [', '.join(x) for x in enrichment_dataframe_subset['overlapping_genes']]
		enrichment_dataframe_subset[target_label.title()] = ['{nr_overlapping_genes} {geneset} '.format(**rowData)+target_label+'s' for index, rowData in enrichment_dataframe_subset.iterrows()]
		# enrichment_dataframe[target_label.title()] = ['<span class="gene-tooltip">{nr_overlapping_genes} {geneset} '.format(**rowData)+target_label+'s<div class="gene-tooltip-text">{overlapping_genes}</div></span>'.format(**rowData) for index, rowData in enrichment_dataframe.iterrows()]

		# Convert to HTML
		pd.set_option('max.colwidth', -1)
		html_table = enrichment_dataframe_subset.head(50)[['Rank', source_label, 'P-value', 'FDR', target_label.title()]].to_html(escape=False, index=False, classes='w-100')
		html_results = '<div style="max-height: 200px; overflow-y: scroll;">{}</div>'.format(html_table)

		# Add CSS
		display(HTML('<style>.w-100{width: 100%;} .text-left th{text-align: left !important;}</style>'))
		display(HTML('<style>.slick-cell{overflow: visible;}.gene-tooltip{text-decoration: underline; text-decoration-style: dotted;}.gene-tooltip .gene-tooltip-text{visibility: hidden; position: absolute; left: 60%; width: 250px; z-index: 1000; text-align: center; background-color: black; color: white; padding: 5px 10px; border-radius: 5px;} .gene-tooltip:hover .gene-tooltip-text{visibility: visible;} .gene-tooltip .gene-tooltip-text::after {content: " ";position: absolute;bottom: 100%;left: 50%;margin-left: -5px;border-width: 5px;border-style: solid;border-color: transparent transparent black transparent;}</style>'))

		# Display gene set
		display(Markdown('### A. TargetScan (experimentally validated targets)' if gene_set_library == 'TargetScan_microRNA_2017' else '### B. miRTarBase (experimentally validated targets)'))

		# Display table
		display(HTML(html_results))

#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(enrichr_results, signature_label):

	# Initialize results
	results = []

	# Loop through genesets
	for geneset in ['upregulated', 'downregulated']:

		# Append ChEA results
		enrichment_dataframe = get_enrichr_results(enrichr_results[geneset]['userListId'], gene_set_libraries=['TargetScan_microRNA_2017', 'miRTarBase_2017'])
		enrichment_dataframe['geneset'] = geneset
		results.append(enrichment_dataframe)

	# Concatenate results
	tf_dataframe = pd.concat(results)

	return {'tf_dataframe': tf_dataframe, 'signature_label': signature_label}

#############################################
########## 2. Plot
#############################################

def plot(mirna_enrichment_results, plot_counter):

	results_table(mirna_enrichment_results['tf_dataframe'].copy(), source_label='miRNA', target_label='target')

	# Figure Legend
	display(Markdown('** Table '+plot_counter('table')+' | miRNA Enrichment Analysis Results. **The figure contains browsable tables displaying the results of the miRNA enrichment analysis generated using Enrichr. Every row represents a miRNA; significant miRNAs are highlighted in bold. A. displays results generated using the TargetScan library, B. displays results generated using the miRTarBase library.'.format(**locals())))