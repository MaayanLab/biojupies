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
import numpy as np
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

def run(signature, nr_genes=500, signature_label=''):

	# Define results
	l1000cds2_results = {'signature_label': signature_label}

	# Define upperGenes Function
	upperGenes = lambda genes: [gene.upper() for gene in genes]

	# Get Data
	data = {"upGenes":upperGenes(signature.index[:nr_genes]),"dnGenes":upperGenes(signature.index[-nr_genes:])}

	# Loop through aggravate:
	for aggravate in [True, False]:

		# Send to API
		config = {"aggravate":aggravate,"searchMethod":"geneSet","share":True,"combination":False,"db-version":"latest"}
		r = requests.post('http://amp.pharm.mssm.edu/L1000CDS2/query',data=json.dumps({"data":data,"config":config}),headers={'content-type':'application/json'})
		label = 'mimic' if aggravate else 'reverse'

		# Add results
		resGeneSet = r.json()
		l1000cds2_dataframe = l1000cds2_dataframe = pd.DataFrame(resGeneSet['topMeta'])[['cell_id', 'pert_desc', 'pert_dose', 'pert_dose_unit', 'pert_id', 'pert_time', 'pert_time_unit', 'pubchem_id', 'score', 'sig_id']].replace('-666', np.nan)
		l1000cds2_results[label] = {'url': 'http://amp.pharm.mssm.edu/L1000CDS2/#/result/{}'.format(resGeneSet['shareId']), 'table': l1000cds2_dataframe}

	# Return
	return l1000cds2_results

#############################################
########## 2. Plot
#############################################

def plot(l1000cds2_results, nr_drugs=7, height=300):
	# Links
	if l1000cds2_results['signature_label']:
		display(Markdown('\n### {signature_label} signature:'.format(**l1000cds2_results)))
	display(Markdown(' **L1000CDS<sup>2</sup> Links:**'))
	display(Markdown(' *Mimic Signature Query Results*: {url}'.format(**l1000cds2_results['mimic'])))
	display(Markdown(' *Reverse Signature Query Results*: {url}'.format(**l1000cds2_results['reverse'])))

	# Bar charts
	fig = tools.make_subplots(rows=1, cols=2, print_grid=False);
	for i, direction in enumerate(['mimic', 'reverse']):
		drug_counts = l1000cds2_results[direction]['table'].groupby('pert_desc').size().sort_values(ascending=False).iloc[:nr_drugs].iloc[::-1]

		# Get Bar
		bar = go.Bar(
			x=drug_counts.values,
			y=drug_counts.index,
			orientation='h',
			name=direction.title(),
			hovertext=drug_counts.index,
			hoverinfo='text',
			marker={'color': '#FF7F50' if direction=='mimic' else '	#9370DB'}
		)
		fig.append_trace(bar, 1, i+1)
		
		# Get text
		text = go.Scatter(
			 x=[max(bar['x'])/50 for x in range(len(bar['y']))],
			 y=bar['y'],
			 mode='text',
			 hoverinfo='none',
			 showlegend=False,
			 text=drug_counts.index,
			 textposition="middle right",
			 textfont={'color': 'black'}
		)
		fig.append_trace(text, 1, i+1)

	fig['layout'].update(height=height, title='<b>L1000CDS<sup>2</sup> | Small Molecule Query</b><br><i>Top small molecules</i>', hovermode='closest')
	fig['layout']['xaxis1'].update(domain=[0,0.5])
	fig['layout']['xaxis1'].update(title='<br>Count')
	fig['layout']['xaxis2'].update(title='<br>Count')
	fig['layout']['xaxis2'].update(domain=[0.5,1])
	fig['layout']['yaxis1'].update(showticklabels=False)
	fig['layout']['yaxis2'].update(showticklabels=False)
	fig['layout']['margin'].update(l=10, t=95, r=0, b=45, pad=5)
	return iplot(fig)

