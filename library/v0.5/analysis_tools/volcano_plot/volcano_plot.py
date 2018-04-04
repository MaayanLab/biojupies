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
from IPython.display import display, Markdown

##### 2. Other libraries #####


#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

def plot_2D_scatter(x, y, text='', title='', xlab='', ylab='', hoverinfo='text', color='black', colorscale='Blues', size=8, showscale=False, symmetric_x=False, symmetric_y=False, pad=0.5, hline=False, vline=False, return_trace=False, labels=False):
	range_x = [-max(abs(x))-pad, max(abs(x))+pad]if symmetric_x else []
	range_y = [-max(abs(y))-pad, max(abs(y))+pad]if symmetric_y else []
	trace = go.Scattergl(x=x, y=y, mode='markers', text=text, hoverinfo=hoverinfo, marker={'color': color, 'colorscale': colorscale, 'showscale': showscale, 'size': size})
	if return_trace:
		return trace
	else:
		annotations = [
			{'x': 0.25, 'y': 1.07, 'text':'<span style="color: blue; font-size: 10pt; font-weight: 600;">Down-regulated in '+labels[-1]+'</span>', 'showarrow': False, 'xref': 'paper', 'yref': 'paper', 'xanchor': 'center'},
			{'x': 0.75, 'y': 1.07, 'text':'<span style="color: red; font-size: 10pt; font-weight: 600;">Up-regulated in '+labels[-1]+'</span>', 'showarrow': False, 'xref': 'paper', 'yref': 'paper', 'xanchor': 'center'}
		] if labels else []
		layout = go.Layout(title=title, xaxis={'title': xlab, 'range': range_x}, yaxis={'title': ylab, 'range': range_y}, hovermode='closest', annotations=annotations)
		fig = go.Figure(data=[trace], layout=layout)
		return iplot(fig)

#############################################
########## 1. Run
#############################################

def run(signature, signature_label='', pvalue_threshold=0.05, logfc_threshold=1.5):

	# Loop through signature
	color = []
	text = []
	for index, rowData in signature.iterrows():

		# Text
		text.append('<b>'+index+'</b><br>Avg Expression = '+str(round(rowData['AveExpr'], ndigits=2))+'<br>logFC = '+str(round(rowData['logFC'], ndigits=2))+'<br>p = '+'{:.2e}'.format(rowData['P.Value'])+'<br>FDR = '+'{:.2e}'.format(rowData['adj.P.Val']))

		# Color
		if rowData['P.Value'] < pvalue_threshold:
		# if rowData['adj.P.Val'] < 0.05:
			if rowData['logFC'] < -logfc_threshold:
				color.append('blue')
			elif rowData['logFC'] > logfc_threshold:
				color.append('red')
			else:
				color.append('black')

		else:
			color.append('black')
	
	# Return 
	volcano_plot_results = {'x': signature['logFC'], 'y': -np.log10(signature['P.Value']), 'text':text, 'color': color, 'signature_label': signature_label}
	return volcano_plot_results

#############################################
########## 2. Plot
#############################################

def plot(volcano_plot_results, plot_counter):
	spacer = ' '*50
	plot_2D_scatter(
		x=volcano_plot_results['x'],
		y=volcano_plot_results['y'],
		text=volcano_plot_results['text'],
		color=volcano_plot_results['color'],
		symmetric_x=True,
		xlab='logFC',
		ylab='log10P',
		title='<b>{volcano_plot_results[signature_label]} Signature | Volcano Plot</b>'.format(**locals()),
		labels=volcano_plot_results['signature_label'].split(' vs ')
	)

	# Figure Legend
	display(Markdown('** Figure '+plot_counter()+' | Volcano Plot. **The figure contains an interactive scatter plot which displays the log2-fold changes and statistical significance of each gene calculated by performing a differential gene expression analysis. Every point in the plot represents a gene. Red points indicate significantly up-regulated genes, blue points indicate down-regulated genes. Additional information for each gene is available by hovering over it.'.format(**locals())))
