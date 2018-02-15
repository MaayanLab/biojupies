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

def run(signature, topN=10, signature_label=''):
 
	if topN:
		signature = pd.concat([signature.iloc[:topN], signature.iloc[-topN:]]).drop(['t', 'B'], axis=1)
		signature['logFC'] = ['{:.3}'.format(x) for x in signature['logFC']]
		signature['AveExpr'] = ['{:.3}'.format(x) for x in signature['AveExpr']]
		signature['P.Value'] = ['{:.2}'.format(x) for x in signature['P.Value']]
		signature['adj.P.Val'] = ['{:.2}'.format(x) for x in signature['adj.P.Val']]
	return signature

#############################################
########## 2. Plot
#############################################

def plot(signature):
	signature.index.name='Gene Symbol'
	# return qgrid.show_grid(signature, grid_options={'maxVisibleRows': 5})
	return display(HTML(signature.to_html()))
