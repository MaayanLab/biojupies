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

def run(signature, topN=30, signature_label=''):
 
	if topN:
		# signature = pd.concat([signature.iloc[:topN], signature.iloc[-topN:]]).drop(['t', 'B'], axis=1).sort_values('P.Value')
		signature = signature.sort_values('P.Value').iloc[:topN]
		signature['logFC'] = ['{:.3}'.format(x) for x in signature['logFC']]
		signature['AveExpr'] = ['{:.3}'.format(x) for x in signature['AveExpr']]
		signature['P.Value'] = ['{:.3}'.format(x) for x in signature['P.Value']]
		signature['adj.P.Val'] = ['{:.3}'.format(x) for x in signature['adj.P.Val']]
	return signature

#############################################
########## 2. Plot
#############################################

def plot(signature):
	signature.index.name='Gene Symbol'
	# return qgrid.show_grid(signature, grid_options={'maxVisibleRows': 5})
	return display(HTML(signature.rename(columns={'logFC': 'logFoldChange', 'AveExpr': 'Average Expression', 'P.Value': 'P-value', 'adj.P.Val': 'Adjusted P-value (FDR)'}).drop(['B', 't'], axis=1).to_html()))
