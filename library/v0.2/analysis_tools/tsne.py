#################################################################
#################################################################
############### tsne 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
from sklearn.manifold import TSNE
import plotly.graph_objs as go
from plotly.offline import iplot

##### 2. Other libraries #####

#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(dataset, dimensions=3, nr_genes=2500, normalization='zscore', color_by=None, color_type='categorical', colorscale='Viridis'):

	# Get expression
	expression_dataframe = dataset[normalization]

	# Filter
	expression_dataframe = expression_dataframe.loc[expression_dataframe.var(axis=1).sort_values(ascending=False).index[:nr_genes]]

	# Run tsne
	tsne=TSNE(n_components=3).fit_transform(expression_dataframe.T)
	tsne_dim = [[x[i] for x in tsne] for i in range(3)]

	# Return
	tsne_results = {'tsne': tsne_dim, 'sample_metadata': dataset['sample_metadata'].loc[expression_dataframe.columns], 'color_by': color_by, 'color_type': color_type, 'nr_genes': nr_genes, 'colorscale': colorscale}
	return tsne_results

#############################################
########## 2. Plot
#############################################

def plot(tsne_results):

	# Get results
	tsne = tsne_results['tsne']
	sample_metadata = tsne_results['sample_metadata']
	color_by = tsne_results.get('color_by')
	color_type = tsne_results.get('color_type')
	color_column = tsne_results['sample_metadata'][color_by] if color_by else None
	colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928']
	sample_titles = ['<b>{}</b><br>'.format(index)+'<br>'.join('<i>{key}</i>: {value}'.format(**locals()) for key, value in rowData.items()) for index, rowData in sample_metadata.iterrows()]

	if not color_by:
		marker = dict(size=15)
		trace = go.Scatter3d(x=tsne[0],
							 y=tsne[1],
							 z=tsne[2],
							 mode='markers',
							 hoverinfo='text',
							 text=sample_titles,
							 marker=marker)
		data = [trace]
	elif color_by and color_type == 'continuous':
		marker = dict(size=15, color=color_column, colorscale=tsne_results['colorscale'], showscale=True)
		trace = go.Scatter3d(x=tsne[0],
							 y=tsne[1],
							 z=tsne[2],
							 mode='markers',
							 hoverinfo='text',
							 text=sample_titles,
							 marker=marker)
		data = [trace]
	elif color_by and color_type == 'categorical':
		# Get unique categories
		unique_categories = color_column.unique()

		# Define empty list
		data = []
			
		# Loop through the unique categories
		for i, category in enumerate(unique_categories):

			# Get the color corresponding to the category
			category_color = colors[i]

			# Get the indices of the samples corresponding to the category
			category_indices = [i for i, sample_category in enumerate(color_column) if sample_category == category]
			
			# Create new trace
			trace = go.Scatter3d(x=tsne[0][category_indices],
								 y=tsne[1][category_indices],
								 z=tsne[2][category_indices],
								 mode='markers',
								 hoverinfo='text',
								 text=[sample_titles[x] for x in category_indices],
								 name = category,
								 marker=dict(size=15, color=category_color))
			
			# Append trace to data list
			data.append(trace)
	
	colored = '' if str(color_by) == 'None' else '<i>, colored by {}</i>'.format(color_by)
	layout = go.Layout(title='<b>t-SNE Analysis | Scatter Plot</b><br><i>Top {} variable genes</i>'.format(tsne_results['nr_genes'])+colored, hovermode='closest', margin=go.Margin(l=0,r=0,b=0,t=50), width=900,
		scene=dict(xaxis=dict(title='t-SNE1'), yaxis=dict(title='t-SNE2'),zaxis=dict(title='t-SNE3')))
	fig = go.Figure(data=data, layout=layout)

	return iplot(fig)
