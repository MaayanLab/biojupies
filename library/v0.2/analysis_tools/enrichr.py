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
		selectedColumns = ['term_name','zscore','combined_score','pvalue', 'FDR'] if not overlappingGenes else ['term_name','zscore','combined_score','FDR', 'overlapping_genes']
		resultDataframe = resultDataframe.loc[:,selectedColumns]
		resultDataframe['gene_set_library'] = gene_set_library
		results.append(resultDataframe)
	concatenatedDataframe = pd.concat(results)
	return concatenatedDataframe

def run(signature, nr_genes, libraries=['GO_Biological_Process_2017b', 'GO_Molecular_Function_2017b', 'KEGG_2016']):

	# Get genesets
	genesets = {}
	genesets['upregulated'] = signature.index[-nr_genes:]
	genesets['downregulated'] = signature.index[:nr_genes]

	# Submit to Enrichr
	enrichr_ids = {geneset_label: submit_enrichr_geneset(geneset=geneset) for geneset_label, geneset in genesets.items()}

	# Get enrichment results
	enrichr_results = {geneset: {'url': 'https://amp.pharm.mssm.edu/Enrichr/enrich?dataset='+ids['shortId'], 'table': get_enrichr_results(ids['userListId'], libraries)} for geneset, ids in enrichr_ids.items()}
	return enrichr_results

#############################################
########## 2. Plot
#############################################

def plot_library_barchart(enrichr_results, gene_set_library):
    fig = tools.make_subplots(rows=1, cols=2, print_grid=False);
    for i, geneset in enumerate(['upregulated', 'downregulated']):
        # Get dataframe
        enrichment_dataframe = enrichr_results[geneset]['table']
        plot_dataframe = enrichment_dataframe[enrichment_dataframe['gene_set_library'] == gene_set_library].sort_values('combined_score').iloc[:5].iloc[::-1]
        
        # Get Bar
        bar = go.Bar(
            x=-plot_dataframe['combined_score'],
            y=plot_dataframe['term_name'],
            orientation='h',
            name=geneset.title(),
            hoverinfo='none',
            marker={'color': 'red' if geneset=='upregulated' else 'blue'}
        )
        fig.append_trace(bar, 1, i+1)
        
        # Get text
        text = go.Scatter(
            x=[1 for x in range(len(bar['y']))],
            y=bar['y'],
            mode='text',
            text=plot_dataframe['term_name'],
            hoverinfo='none',
            showlegend=False,
            textposition="middle right",
            textfont={'color': 'white'}
        )
        fig.append_trace(text, 1, i+1)
        
    fig['layout'].update(height=250, title='<b>'+gene_set_library.replace('_', ' ')+'</b>')
    fig['layout']['xaxis1'].update(domain=[0,0.5])
    fig['layout']['xaxis2'].update(domain=[0.5,1])
    fig['layout']['yaxis1'].update(showticklabels=False)
    fig['layout']['yaxis2'].update(showticklabels=False)
    fig['layout']['margin'].update(l=0, t=40, r=0, b=30)
    return iplot(fig)

def plot(enrichr_results):
	display(Markdown('**Enrichr Links:**'))
	display(Markdown('*Upregulated Genes*: {url}'.format(**enrichr_results['upregulated'])))
	display(Markdown('*Downregulated Genes*: {url}'.format(**enrichr_results['downregulated'])))
	enrichment_dataframe = pd.concat([enrichr_results['upregulated']['table'], enrichr_results['downregulated']['table']])
	for gene_set_library in enrichment_dataframe['gene_set_library'].unique():
		plot_library_barchart(enrichr_results, gene_set_library)

