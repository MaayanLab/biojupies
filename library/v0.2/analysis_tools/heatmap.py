#################################################################
#################################################################
############### DE 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import seaborn as sns
import plotly.graph_objs as go
from plotly.offline import iplot
import matplotlib.pyplot as plt
import scipy.stats as ss

##### 2. Other libraries #####


#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(dataset, normalization='zscore', nr_genes=500):
 
	# Get clustering data
	expression_dataframe = dataset[normalization]

	# Cases
	if normalization == 'zscore':
		z_score = None
	else:
		z_score = 0

	# Filter
	filtered_dataframe = expression_dataframe.loc[expression_dataframe.var(axis=1).sort_values(ascending=False).index[:nr_genes]]

	# Cluster
	cluster_data = sns.clustermap(filtered_dataframe, z_score=z_score);
	plt.close();

	# Get percentile for 0
	perc = ss.percentileofscore([value for col in cluster_data.data2d.values for value in col], -0.15, kind='rank')/100

	# Get results
	heatmap_results = {'clustering': cluster_data, 'percentile': perc}
	return heatmap_results

#############################################
########## 2. Plot
#############################################

def plot(heatmap_results):

	# Plot
	trace = go.Heatmap(x=heatmap_results['clustering'].data2d.columns, y=heatmap_results['clustering'].data2d.index, z=heatmap_results['clustering'].data2d.values, colorscale=[[0, 'blue'], [heatmap_results['percentile'], 'white'], [1.0, 'red']])
	layout = go.Layout(title='<b>Clustered Heatmap</b>', margin=go.Margin(l=100,r=0,b=100,t=50))
	fig = go.Figure(data=[trace], layout=layout)
	return iplot(fig)
