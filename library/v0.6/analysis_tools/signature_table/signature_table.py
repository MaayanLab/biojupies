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

def run(signature, signature_label=''):
	return signature.copy()

#############################################
########## 2. Plot
#############################################

def plot(signature, plot_counter):
	# signature.index = ['<a href="http://www.genecards.org/cgi-bin/carddisp.pl?gene={x}" target="_blank">{x}</a>'.format(**locals()) for x in signature.index] # human
	signature.index = ['<a href="http://amp.pharm.mssm.edu/Harmonizome/gene/'+x.upper()+'" target="_blank">'+x+'</a>' for x in signature.index] # mouse
	signature.index = [index.replace('target="_blank">', 'target="_blank"><b>*').replace('</a>', '</b></a>') if rowData['adj.P.Val'] < 0.05 else index for index, rowData in signature.iterrows()] # mouse
	signature.index.name = 'Gene'
	signature['logFC'] = round(signature['logFC'], ndigits=2)
	signature['AveExpr'] = round(signature['AveExpr'], ndigits=2)
	html_table = signature.rename(columns={'gene_symbol': 'Gene', 'P.Value': 'P-value', 'adj.P.Val': 'FDR'}).drop(['t', 'B'], axis=1).sort_values('P-value').head(100).to_html(escape=False, classes='w-100')
	html_results = '<div style="max-height: 200px; overflow-y: scroll;">{}</div>'.format(html_table)
	display(HTML('<style>.w-100{width: 100%;}</style>'))
	# display(qgrid.show_grid(signature.rename(columns={'gene_symbol': 'Gene', 'P.Value': 'P-value', 'adj.P.Val': 'FDR'}).drop(['t', 'B'], axis=1), grid_options={'maxVisibleRows': 4}))
	display(HTML(html_results))

	# Figure Legend
	display(Markdown('** Table '+plot_counter('table')+' | Differential Expression Table.** The figure displays a browsable table containing the gene expression signature generated from a differential gene expression analysis. Every row of the table represents a gene; the columns display the estimated measures of differential expression. Links to external resources containing additional information for each gene are also provided'.format(**locals())))
