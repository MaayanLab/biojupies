#################################################################
#################################################################
############### DE 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import pandas as pd
import qgrid
from IPython.display import display, HTML

##### 2. Other libraries #####


#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(signature, signature_label=''):
	return signature.copy()

#############################################
########## 2. Plot
#############################################

def plot(signature):
	# signature.index = ['<a href="http://www.genecards.org/cgi-bin/carddisp.pl?gene={x}" target="_blank">{x}</a>'.format(**locals()) for x in signature.index] # human
	signature.index = ['<a href="http://amp.pharm.mssm.edu/Harmonizome/gene/{x}" target="_blank">{x}</a>'.format(**locals()) for x in signature.index] # mouse
	signature.index.name = 'Gene'
	html_table = signature.rename(columns={'gene_symbol': 'Gene', 'P.Value': 'P-value', 'adj.P.Val': 'FDR'}).drop(['t', 'B'], axis=1).sort_values('P-value').head(50).to_html(escape=False, classes='w-100')
	html_results = '<div style="max-height: 200px; overflow-y: scroll;">{}</div>'.format(html_table)
	display(HTML('<style>.w-100{width: 100%;}</style>'))
	# display(qgrid.show_grid(signature.rename(columns={'gene_symbol': 'Gene', 'P.Value': 'P-value', 'adj.P.Val': 'FDR'}).drop(['t', 'B'], axis=1), grid_options={'maxVisibleRows': 4}))
	display(HTML(html_results))
