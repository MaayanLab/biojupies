#################################################################
#################################################################
############### Generate Signature
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import os
import requests
import json
import pandas as pd
from plotly import tools
from plotly.offline import iplot
import plotly.graph_objs as go
from IPython.display import display, Markdown, HTML

#######################################################
#######################################################
########## S1. Enrichr
#######################################################
#######################################################

#############################################
########## 1. Get Enrichr Results
#############################################

def get_enrichr_results(user_list_id, gene_set_libraries, overlappingGenes=True):
	ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/enrich'
	query_string = '?userListId=%s&backgroundType=%s'
	results = []
	for gene_set_library, label in gene_set_libraries.items():
		response = requests.get(
                    ENRICHR_URL +
                   	query_string % (user_list_id, gene_set_library)
                )
		if not response.ok:
			raise Exception('Error fetching enrichment results')

		data = json.loads(response.text)
		resultDataframe = pd.DataFrame(data[gene_set_library], columns=[
		                               'rank', 'term_name', 'pvalue', 'zscore', 'combined_score', 'overlapping_genes', 'FDR', 'old_pvalue', 'old_FDR'])
		selectedColumns = ['term_name', 'zscore', 'combined_score', 'pvalue', 'FDR'] if not overlappingGenes else [
			'term_name', 'zscore', 'combined_score', 'FDR', 'pvalue', 'overlapping_genes']
		resultDataframe = resultDataframe.loc[:, selectedColumns]
		resultDataframe['gene_set_library'] = label
		results.append(resultDataframe)
	concatenatedDataframe = pd.concat(results)
	return concatenatedDataframe

#############################################
########## 2. Plot Enrichment Barchart
#############################################

def plot_library_barchart(enrichr_results, gene_set_library, signature_label, nr_genesets, height):
	fig = tools.make_subplots(rows=1, cols=2, print_grid=False)
	for i, geneset in enumerate(['upregulated', 'downregulated']):
		# Get dataframe
		enrichment_dataframe = enrichr_results[geneset]
		plot_dataframe = enrichment_dataframe[enrichment_dataframe['gene_set_library'] == gene_set_library].sort_values(
			'combined_score', ascending=False).iloc[:nr_genesets].iloc[::-1]

		# Format
		plot_dataframe['overlapping_genes'] = [', '.join(x) if len(x) <= 5 else ', '.join(
			x[:5])+', + '+str(len(x)-5)+' others' for x in plot_dataframe['overlapping_genes']]

		# Get Bar
		bar = go.Bar(
			x=plot_dataframe['combined_score'],
			y=plot_dataframe['term_name'],
			orientation='h',
			name=geneset.title(),
			showlegend=False,
			hovertext=['<b>{term_name}</b><br><b>P-value</b>: <i>{pvalue:.2}</i><br><b>FDR</b>: <i>{FDR:.2}</i><br><b>Z-score</b>: <i>{zscore:.3}</i><br><b>Combined score</b>: <i>{combined_score:.3}</i><br><b>Genes</b>: <i>{overlapping_genes}</i><br>'.format(
				**rowData) for index, rowData in plot_dataframe.iterrows()],
			hoverinfo='text',
			marker={'color': '#FA8072' if geneset == 'upregulated' else '	#87CEFA'}
		)
		fig.append_trace(bar, 1, i+1)

		# Get text
		text = go.Scatter(
			x=[max(bar['x'])/50 for x in range(len(bar['y']))],
			y=bar['y'],
			mode='text',
			hoverinfo='none',
			showlegend=False,
			text=['*<b>{}</b>'.format(rowData['term_name']) if rowData['FDR'] < 0.1 else '{}'.format(
				rowData['term_name']) for index, rowData in plot_dataframe.iterrows()],
			textposition="middle right",
			textfont={'color': 'black'}
		)
		fig.append_trace(text, 1, i+1)

	# Get annotations
	labels = signature_label.split('vs ')
	annotations = [
		{'x': 0.25, 'y': 1.12, 'text': '<span style="color: #FA8072; font-size: 10pt; font-weight: 600;">Up-regulated in ' +
			labels[-1]+'</span>', 'showarrow': False, 'xref': 'paper', 'yref': 'paper', 'xanchor': 'center'},
		{'x': 0.75, 'y': 1.12, 'text': '<span style="color: #87CEFA; font-size: 10pt; font-weight: 600;">Down-regulated in ' +
			labels[-1]+'</span>', 'showarrow': False, 'xref': 'paper', 'yref': 'paper', 'xanchor': 'center'}
	] if signature_label else []

	# Get title
	title = signature_label + ' | ' + gene_set_library

	fig['layout'].update(height=height, title='<b>{}</b>'.format(title),
	                     hovermode='closest', annotations=annotations)
	fig['layout']['xaxis1'].update(domain=[0, 0.49], title='')
	fig['layout']['xaxis2'].update(domain=[0.51, 1], title='')
	fig['layout']['yaxis1'].update(showticklabels=False)
	fig['layout']['yaxis2'].update(showticklabels=False)
	fig['layout']['margin'].update(l=0, t=65, r=0, b=30)
	return iplot(fig)

#############################################
########## 3. Display Result Table
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
		enrichment_dataframe_subset[source_label] = ['<a href="http://www.mirbase.org/cgi-bin/query.pl?terms={x}" target="_blank">{x}</a>'.format(**locals()) if '-miR-' in x else '<a href="http://amp.pharm.mssm.edu/Harmonizome/gene/{x}" target="_blank">{x}</a>'.format(**locals())for x in enrichment_dataframe_subset[source_label]]
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
		display(Markdown(gene_set_library))

		# Display table
		display(HTML(html_results))
