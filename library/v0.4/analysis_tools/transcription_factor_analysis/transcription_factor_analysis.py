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
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
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

def run(enrichr_results, signature_label, libraries=['ChEA_2016']):
	results = []
	for geneset in ['upregulated', 'downregulated']:
		enrichment_dataframe = get_enrichr_results(enrichr_results[geneset]['userListId'], libraries)
		enrichment_dataframe['geneset'] = geneset
		results.append(enrichment_dataframe)
	transcription_factor_dataframe = pd.concat(results)
	return {'transcription_factor_dataframe': transcription_factor_dataframe, 'signature_label': signature_label}

#############################################
########## 2. Plot
#############################################

def plot(transcription_factor_analysis_results):
	transcription_factor_dataframe = transcription_factor_analysis_results['transcription_factor_dataframe'].copy()
	transcription_factor_dataframe['Transcription Factor'] = [x.split('_')[0] for x in transcription_factor_dataframe['term_name']]
	transcription_factor_dataframe = transcription_factor_dataframe.sort_values('pvalue').rename(columns={'pvalue': 'P-value'}).drop_duplicates('Transcription Factor')
	transcription_factor_dataframe['Rank'] = [x+1 for x in range(len(transcription_factor_dataframe.index))]
	transcription_factor_dataframe['nr_overlapping_genes'] = [len(x) for x in transcription_factor_dataframe['overlapping_genes']]
	transcription_factor_dataframe['overlapping_genes'] = [', '.join(x) for x in transcription_factor_dataframe['overlapping_genes']]
	transcription_factor_dataframe['Targets'] = ['<span class="gene-tooltip">{nr_overlapping_genes} {geneset} targets<div class="gene-tooltip-text"></div></span>'.format(**rowData) for index, rowData in transcription_factor_dataframe.iterrows()]
	transcription_factor_dataframe = transcription_factor_dataframe[['Rank', 'Transcription Factor', 'P-value', 'FDR', 'Targets']]
	transcription_factor_dataframe['Transcription Factor'] = ['<a href="http://www.genecards.org/cgi-bin/carddisp.pl?gene={x}" target="_blank">{x}</a>'.format(**locals()) for x in transcription_factor_dataframe['Transcription Factor']]
	transcription_factor_dataframe['Transcription Factor'] = [rowData['Transcription Factor'].replace('target="_blank">', 'target="_blank"><b>').replace('</a>', '</b></a>') if rowData['FDR'] < 0.1 else rowData['Transcription Factor'] for index, rowData in transcription_factor_dataframe.iterrows()]
	# display(HTML('<style>.slick-cell{overflow: visible;}.gene-tooltip{text-decoration: underline; text-decoration-style: dotted;}.gene-tooltip .gene-tooltip-text{visibility: hidden; position: absolute; max-width: 150px; z-index: 1000; left: -135px; top: 1px; text-align: right; background-color: black; color: white; padding: 5px 10px; border-radius: 5px;} .gene-tooltip:hover .gene-tooltip-text{visibility: visible;}</style>'))
	display(Markdown('### {signature_label} Signature:'.format(**transcription_factor_analysis_results)))
	return display(qgrid.show_grid(transcription_factor_dataframe.set_index('Rank'), grid_options={'maxVisibleRows': 4}))