#################################################################
#################################################################
############### DE 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import requests, json
import pandas as pd
from plotly import tools
from plotly.offline import iplot
import plotly.graph_objs as go
from IPython.display import display, Markdown

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
########## 2. Plot Enrichment Barchart
#############################################

def plot_library_barchart(enrichr_results, gene_set_library, signature_label, nr_genesets, height):
	fig = tools.make_subplots(rows=1, cols=2, print_grid=False);
	for i, geneset in enumerate(['upregulated', 'downregulated']):
		# Get dataframe
		enrichment_dataframe = enrichr_results[geneset]
		plot_dataframe = enrichment_dataframe[enrichment_dataframe['gene_set_library'] == gene_set_library].sort_values('combined_score', ascending=False).iloc[:nr_genesets].iloc[::-1]

		# Format
		plot_dataframe['overlapping_genes'] = [', '.join(x) if len(x) <= 5 else ', '.join(x[:5])+', + '+str(len(x)-5)+' others' for x in plot_dataframe['overlapping_genes']]
		
		# Get Bar
		bar = go.Bar(
			x=plot_dataframe['combined_score'],
			y=plot_dataframe['term_name'],
			orientation='h',
			name=geneset.title(),
			showlegend=False,
			hovertext=['<b>{term_name}</b><br><b>P-value</b>: <i>{pvalue:.2}</i><br><b>FDR</b>: <i>{FDR:.2}</i><br><b>Z-score</b>: <i>{zscore:.3}</i><br><b>Combined score</b>: <i>{combined_score:.3}</i><br><b>Genes</b>: <i>{overlapping_genes}</i><br>'.format(**rowData) for index, rowData in plot_dataframe.iterrows()],
			hoverinfo='text',
			marker={'color': '#FA8072' if geneset=='upregulated' else '	#87CEFA'}
		)
		fig.append_trace(bar, 1, i+1)
		
		# Get text
		text = go.Scatter(
			x=[max(bar['x'])/50 for x in range(len(bar['y']))],
			y=bar['y'],
			mode='text',
			hoverinfo='none',
			showlegend=False,
			text=['*<b>{}</b>'.format(rowData['term_name']) if rowData['FDR'] < 0.1 else '{}'.format(rowData['term_name']) for index, rowData in plot_dataframe.iterrows()],
			textposition="middle right",
			textfont={'color': 'black'}
		)
		fig.append_trace(text, 1, i+1)

	# Get annotations
	labels = signature_label.split('vs ')
	annotations = [
		{'x': 0.25, 'y': 1.12, 'text':'<span style="color: #FA8072; font-size: 10pt; font-weight: 600;">Up-regulated in '+labels[-1]+'</span>', 'showarrow': False, 'xref': 'paper', 'yref': 'paper', 'xanchor': 'center'},
		{'x': 0.75, 'y': 1.12, 'text':'<span style="color: #87CEFA; font-size: 10pt; font-weight: 600;">Down-regulated in '+labels[-1]+'</span>', 'showarrow': False, 'xref': 'paper', 'yref': 'paper', 'xanchor': 'center'}
	] if signature_label else []

	# Get title
	title = signature_label+ ' | '+gene_set_library.replace('KEGG_2016', 'KEGG Pathways').replace('WikiPathways_2016', 'WikiPathways').replace('Reactome_2016', 'Reactome Pathways')

	fig['layout'].update(height=height, title='<b>{}</b>'.format(title), hovermode='closest', annotations=annotations)
	fig['layout']['xaxis1'].update(domain=[0,0.49], title='')
	fig['layout']['xaxis2'].update(domain=[0.51,1], title='')
	fig['layout']['yaxis1'].update(showticklabels=False)
	fig['layout']['yaxis2'].update(showticklabels=False)
	fig['layout']['margin'].update(l=0, t=65, r=0, b=30)
	return iplot(fig)

#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(enrichr_results, signature_label, libraries=['KEGG_2016', 'Reactome_2016', 'WikiPathways_2016']):
	pathway_analysis_results = {geneset: get_enrichr_results(enrichr_results[geneset]['userListId'], libraries) for geneset in ['upregulated', 'downregulated']}
	pathway_analysis_results['signature_label'] = signature_label
	return pathway_analysis_results

#############################################
########## 2. Plot
#############################################

def plot(pathway_analysis_results, plot_counter):
	if pathway_analysis_results['signature_label']:
		pass# display(Markdown('### {signature_label} signature:'.format(**pathway_analysis_results)))
	enrichment_dataframe = pd.concat([pathway_analysis_results['upregulated'], pathway_analysis_results['downregulated']])
	for gene_set_library in enrichment_dataframe['gene_set_library'].unique():
		plot_library_barchart(pathway_analysis_results, gene_set_library, pathway_analysis_results['signature_label'], 10, 300)

	# Figure Legend
	display(Markdown('** Figure '+plot_counter()+' | Pathway Enrichment Analysis Results.** The figure contains interactive bar charts displaying the results of the pathway enrichment analysis generated using Enrichr. The x axis indicates the enrichment score for each term. Significant terms are highlighted in bold. Additional information about enrichment results is available by hovering over each bar.'.format(**locals())))
