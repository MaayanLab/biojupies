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
	signature.index = ['<a href="http://www.informatics.jax.org/searchtool/Search.do?query={x}" target="_blank">{x}</a>'.format(**locals()) for x in signature.index] # mouse
	signature.index.name = 'Gene'
	display(qgrid.show_grid(signature.rename(columns={'gene_symbol': 'Gene', 'P.Value': 'P-value', 'adj.P.Val': 'FDR'}).drop(['t', 'B'], axis=1), grid_options={'maxVisibleRows': 4}))
