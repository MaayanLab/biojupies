#################################################################
#################################################################
############### PCA 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
from sklearn.decomposition import PCA
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

def run(dataset, dimensions=3, nr_genes=1000, normalization='zscore', color_by=None, color_type=None):

	# Get expression
	expression_dataframe = dataset[normalization]

	# Filter
	expression_dataframe = expression_dataframe.loc[expression_dataframe.var(axis=1).sort_values(ascending=False).index[:nr_genes]]

	# Run PCA
	pca=PCA(n_components=3)
	pca.fit(expression_dataframe)

	# Get Variance
	var_explained = ['PC'+str((i+1))+'('+str(round(e*100, 1))+'% var. explained)' for i, e in enumerate(pca.explained_variance_ratio_)]

	# Return
	pca_results = {'pca': pca, 'var_explained': var_explained, 'sample_titles': expression_dataframe.columns, 'color_column': dataset['sample_metadata'][color_by] if color_by else None, 'color_by': color_by, 'color_type': color_type, 'nr_genes': nr_genes}
	return pca_results

#############################################
########## 2. Plot
#############################################

def plot(pca_results):

	# Get results
	pca = pca_results['pca']
	var_explained = pca_results['var_explained']
	sample_titles = pca_results['sample_titles']
	color_by = pca_results.get('color_by')
	color_type = pca_results.get('color_type')
	color_column = pca_results.get('color_column')
	# colors = ['red', 'blue', 'orange', 'purple', 'turkey', 'chicken', 'thanksigiving', 'orange', 'red', 'green']
	colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928']

	if not color_by:
		marker = dict(size=15)
		trace = go.Scatter3d(x=pca.components_[0],
							 y=pca.components_[1],
							 z=pca.components_[2],
							 mode='markers',
							 hoverinfo='text',
							 text=sample_titles,
							 marker=marker)
		data = [trace]
	elif color_by and color_type == 'continuous':
		marker = dict(size=15, color=color_column, colorscale="Viridis", showscale=True)
		trace = go.Scatter3d(x=pca.components_[0],
							 y=pca.components_[1],
							 z=pca.components_[2],
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
			trace = go.Scatter3d(x=pca.components_[0][category_indices],
								 y=pca.components_[1][category_indices],
								 z=pca.components_[2][category_indices],
								 mode='markers',
								 hoverinfo='text',
								 text=sample_titles[category_indices],
								 name = category,
								 marker=dict(size=15, color=category_color))
			
			# Append trace to data list
			data.append(trace)
	
	colored = '' if str(color_by) == 'None' else '<i>, colored by {}</i>'.format(color_by)
	layout = go.Layout(title='<b>PCA Analysis | Scatter Plot</b><br><i>Top {} variable genes</i>'.format(pca_results['nr_genes'])+colored, hovermode='closest', margin=go.Margin(l=0,r=0,b=0,t=50), width=900,
		scene=dict(xaxis=dict(title=var_explained[0]), yaxis=dict(title=var_explained[1]),zaxis=dict(title=var_explained[2])))
	fig = go.Figure(data=data, layout=layout)

	return iplot(fig)
