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
import requests, json
from plotly.offline import iplot
import plotly.graph_objs as go
from IPython.display import display, Markdown
import numpy as np


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

def run(signature_A, signature_B, enrichr_results, libraries=['GO_Biological_Process_2017b', 'GO_Molecular_Function_2017b']):

	# Get enrichment results
	results = []
	for signature in [signature_A, signature_B]:
		for geneset in ['upregulated', 'downregulated']:
			enrichment_dataframe = get_enrichr_results(enrichr_results[signature]['results'][geneset]['userListId'], libraries)
			enrichment_dataframe['signature'] = signature
			enrichment_dataframe['geneset'] = geneset
			results.append(enrichment_dataframe)

	# Concatenate
	enrichment_results = pd.concat(results)
	return enrichment_results

#############################################
########## 2. Plot
#############################################

def plot(enrichment_results):

	# Overlapping genes
	enrichment_results['genes'] = [', '.join(x) if len(x) <= 5 else ', '.join(x[:5])+', + '+str(len(x)-5)+' others' for x in enrichment_results['overlapping_genes']]

	# Loop through libraries
	for library in enrichment_results['gene_set_library'].unique()[:1]:

		# Display
		display(Markdown('## Top Common Enrichment Results | {}'.format(library.replace('_', ' ').replace('2017b', ''))))

		# Subset
		library_enrichment_results = enrichment_results[enrichment_results['gene_set_library'] == library]

		i=0
		# Get genesets
		for geneset in library_enrichment_results['geneset'].unique():

			# Get data
			data = []

			# Get subset
			subset = library_enrichment_results[library_enrichment_results['geneset'] == geneset]

			# Group by and sum
			subset_grouped = subset.groupby('term_name')['combined_score'].sum().rename('combined_score').sort_values(ascending=False).to_frame()
			top_terms = subset_grouped.index[:10][::-1]
			subset.set_index('term_name', drop=False, inplace=True)

			# Loop through signatures
			colors = ['lightcoral', 'lightsalmon', 'lightblue', 'paleturquoise']
			for signature in library_enrichment_results['signature'].unique():

				# Get signature subset
				signature_subset = subset[subset['signature'] == signature]

				# Append bar
				bar = go.Bar(
					x=signature_subset.reindex(top_terms)['combined_score'],
					y=top_terms,
					name=signature,
					orientation = 'h',
					hoverinfo='text',
					text = ['<b>{term_name}</b><br><b>P-value</b>: <i>{pvalue:.2}</i><br><b>FDR</b>: <i>{FDR:.2}</i><br><b>Z-score</b>: <i>{zscore:.3}</i><br><b>Combined score</b>: <i>{combined_score:.3}</i><br><b>Genes</b>: <i>{genes}</i><br>'.format(**rowData) for index, rowData in signature_subset.reindex(top_terms).iterrows()],
					marker = dict(
						color = colors[i],
						# line = dict(
							# color = 'rgba(246, 78, 139, 1.0)',
							# width = 3)
					)
				)
				data.append(bar)
				i+=1

				# Append text
				text = go.Scatter(
					x=[max(bar['x'])/50 for x in range(len(bar['y']))],
					y=bar['y'],
					mode='text',
					hoverinfo='none',
					showlegend=False,
					text=['<b>{}</b>'.format(x)+'*'*np.count_nonzero(subset.loc[x, 'FDR'] < 0.1) for x in top_terms],
					textposition="middle right",
					textfont={'color': 'black'}
				)
				data.append(text)

			# Get Layout
			layout = go.Layout(height=300, barmode='stack', title='{} Genes'.format(geneset.title()), hovermode='closest', margin=go.Margin(l=0, t=40, r=0, b=30))

			# Plot figure
			fig = go.Figure(data=data, layout=layout)
			iplot(fig)
