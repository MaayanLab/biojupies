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

def run(genesets, libraries=['GO_Biological_Process_2017b', 'ENCODE_TF_ChIP-seq_2015', 'KEGG_2016', 'ARCHS4_TFs_Coexp', 'MGI_Mammalian_Phenotype_2017', 'Allen_Brain_Atlas_up']):

	# Submit to Enrichr
	enrichr_ids = {geneset_label: submit_enrichr_geneset(geneset=geneset) for geneset_label, geneset in genesets.items()}

	# Get Results
	return enrichr_ids

#############################################
########## 2. Plot
#############################################

def plot(enrichr_ids, plot_counter):
	return display(Markdown('##### Enrichment Results:'+''.join(['\n * *{key}*: https://amp.pharm.mssm.edu/Enrichr/enrich?dataset={value[shortId]}'.format(**locals()) for key, value in enrichr_ids.items()])))

