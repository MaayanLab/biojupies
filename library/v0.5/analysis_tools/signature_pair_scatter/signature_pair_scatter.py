#################################################################
#################################################################
############### DE 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import numpy as np
import plotly.graph_objs as go
from plotly.offline import iplot

##### 2. Other libraries #####


#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

def plot_2D_scatter(x, y, text='', title='', xlab='', ylab='', hoverinfo='text', color='black', colorscale='Blues', size=8, showscale=False, symmetric_x=False, symmetric_y=False, pad=0.5, hline=False, vline=False, return_trace=False):
	range_x = [-max(abs(x))-pad, max(abs(x))+pad]if symmetric_x else []
	range_y = [-max(abs(y))-pad, max(abs(y))+pad]if symmetric_y else []
	trace = go.Scattergl(x=x, y=y, mode='markers', text=text, hoverinfo=hoverinfo, marker={'color': color, 'colorscale': colorscale, 'showscale': showscale, 'size': size})
	if return_trace:
		return trace
	else:
		layout = go.Layout(title=title, xaxis={'title': xlab, 'range': range_x}, yaxis={'title': ylab, 'range': range_y}, hovermode='closest')
		fig = go.Figure(data=[trace], layout=layout)
		return iplot(fig)

#############################################
########## 1. Run
#############################################

def run(signature_A, signature_B, signatures, col='logFC'):

	# Merge signatures
	merged_dataframe = signatures[signature_A].merge(signatures[signature_B], left_index=True, right_index=True, suffixes=('_'+signature_A, '_'+signature_B))#[[signature_A, signature_B]]

	# Get text
	summary = lambda x, gene: '<span style="font-style: italic;">'+x+'</span><br>    • logFC: '+'{:.2e}'.format(merged_dataframe.loc[gene,'logFC_'+x])+'<br>    • P-value: '+'{:.2e}'.format(merged_dataframe.loc[gene,'P.Value_'+x])+'<br>    • FDR: '+'{:.2e}'.format(merged_dataframe.loc[gene,'adj.P.Val_'+x])
	merged_dataframe['text'] = ['<b>'+index+'</b>:<br>'+summary(signature_A, index)+'<br><br>'+summary(signature_B, index) for index, rowData in merged_dataframe.iterrows()]

	# Significance
	colors = {0: 'black', 1: 'red', 2: 'blue', 3: 'purple'}
	merged_dataframe['color'] = [colors[np.sum([1 if rowData['adj.P.Val_'+signature_A] < 0.05 else 0, 2 if rowData['adj.P.Val_'+signature_B] < 0.05 else 0])] for index, rowData in merged_dataframe.iterrows()]

	# Filter
	merged_dataframe = merged_dataframe[['logFC_'+x for x in [signature_A, signature_B]]+['text', 'color']]
	return merged_dataframe

#############################################
########## 2. Plot
#############################################

def plot(signature_pair_scatter):
	plot_2D_scatter(
		x=signature_pair_scatter.iloc[:,0],
		y=signature_pair_scatter.iloc[:,1],
		text=signature_pair_scatter['text'],
		color=signature_pair_scatter['color'],
		showscale=False,
		symmetric_x=True,
		symmetric_y=True,
		xlab=signature_pair_scatter.columns[0],
		ylab=signature_pair_scatter.columns[1],
		title='<b>{} | Signature Comparison</b><br><i>logFC correlation</i>'.format(' & '.join([x.split('_')[-1] for x in signature_pair_scatter.columns[:2]]))
	)
