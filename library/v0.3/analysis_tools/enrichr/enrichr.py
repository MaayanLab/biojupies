#################################################################
#################################################################
############### DE 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import requests
import json
import pandas as pd
from IPython.display import display, Markdown
from plotly import tools
from plotly.offline import iplot
import plotly.graph_objs as go

##### 2. Other libraries #####


#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def get_genesets(signature_dataframe, signature_col, top_n=True, nr_genes=500):
	genesets = {}
	sorted_genes = signature_dataframe.sort_values(signature_col).index
	genesets['upregulated'] = sorted_genes[-500:]
	genesets['downregulated'] = sorted_genes[:500]
	return genesets

def submit_enrichr_geneset(geneset):
	ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/addList'
	genes_str = '\n'.join(geneset)
	payload = {
	'list': (None, genes_str),
	}
	response = requests.post(ENRICHR_URL, files=payload)
	if not response.ok:
		raise Exception('Error analyzing gene list')
	data = json.loads(response.text)
	return data

def get_enrichr_results(user_list_id, gene_set_libraries=['GO_Biological_Process_2017b', 'GO_Cellular_Component_2017b', 'GO_Molecular_Function_2017b'], overlappingGenes=True):
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

def run(signature, geneset_size=500, libraries=['GO_Biological_Process_2017b', 'GO_Molecular_Function_2017b', 'KEGG_2016'], signature_label=''):

	# Get genesets
	genesets = {}
	genesets['upregulated'] = signature.index[:geneset_size]
	genesets['downregulated'] = signature.index[-geneset_size:]

	# Submit to Enrichr
	enrichr_ids = {geneset_label: submit_enrichr_geneset(geneset=geneset) for geneset_label, geneset in genesets.items()}

	# Get enrichment results
	enrichr_results = {geneset: {'url': 'https://amp.pharm.mssm.edu/Enrichr/enrich?dataset='+ids['shortId'], 'table': get_enrichr_results(ids['userListId'], libraries)} for geneset, ids in enrichr_ids.items()}
	enrichr_results['signature_label'] = signature_label
	return enrichr_results

#############################################
########## 2. Plot
#############################################

def plot_library_barchart(enrichr_results, gene_set_library, nr_genesets, height):
    fig = tools.make_subplots(rows=1, cols=2, print_grid=False);
    for i, geneset in enumerate(['upregulated', 'downregulated']):
        # Get dataframe
        enrichment_dataframe = enrichr_results[geneset]['table']
        plot_dataframe = enrichment_dataframe[enrichment_dataframe['gene_set_library'] == gene_set_library].sort_values('combined_score', ascending=False).iloc[:nr_genesets].iloc[::-1]

        # Format
        plot_dataframe['overlapping_genes'] = [', '.join(x) if len(x) <= 5 else ', '.join(x[:5])+', + '+str(len(x)-5)+' others' for x in plot_dataframe['overlapping_genes']]
        
        # Get Bar
        bar = go.Bar(
            x=plot_dataframe['combined_score'],
            y=plot_dataframe['term_name'],
            orientation='h',
            name=geneset.title(),
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

    fig['layout'].update(height=height, title='<b>'+gene_set_library.replace('_', ' ')+'</b>', hovermode='closest')
    fig['layout']['xaxis1'].update(domain=[0,0.5])
    fig['layout']['xaxis2'].update(domain=[0.5,1])
    fig['layout']['yaxis1'].update(showticklabels=False)
    fig['layout']['yaxis2'].update(showticklabels=False)
    fig['layout']['margin'].update(l=0, t=40, r=0, b=30)
    return iplot(fig)

def plot(enrichr_results, nr_genesets=10, height=300):
	if enrichr_results['signature_label']:
		display(Markdown('## {signature_label} signature:'.format(**enrichr_results)))
	display(Markdown(' **Enrichr Links:**'))
	display(Markdown(' *Upregulated Genes*: {url}'.format(**enrichr_results['upregulated'])))
	display(Markdown(' *Downregulated Genes*: {url}'.format(**enrichr_results['downregulated'])))
	enrichment_dataframe = pd.concat([enrichr_results['upregulated']['table'], enrichr_results['downregulated']['table']])
	for gene_set_library in enrichment_dataframe['gene_set_library'].unique():
		plot_library_barchart(enrichr_results, gene_set_library, nr_genesets, height)

