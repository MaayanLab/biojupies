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
import scipy.stats as ss
import warnings
from IPython.display import display, Markdown

##### 2. Other libraries #####

#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(dataset, normalization='logCPM', nr_genes=2500, z_score=True, color_by=None, color_type='categorical'):

	# Get data
	expression_dataframe = dataset[normalization].copy()

	# Filter
	expression_dataframe = expression_dataframe.loc[expression_dataframe.var(axis=1).sort_values(ascending=False).index[:nr_genes]]

	# Z-score
	if z_score == 'True' or z_score == True:
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			expression_dataframe = expression_dataframe.apply(ss.zscore, axis=1)

	# Run tsne
	tsne=TSNE(n_components=3).fit_transform(expression_dataframe.T)
	tsne_dim = [[x[i] for x in tsne] for i in range(3)]

	# Add colors
	if dataset.get('signature_metadata'):
		A_label, B_label = list(dataset['signature_metadata'].keys())[0].split(' vs ')
		col = []
		group_dict = list(dataset['signature_metadata'].values())[0]
		for gsm in dataset['sample_metadata'].index:
			if gsm in group_dict['A']:
				col.append(A_label)
			elif gsm in group_dict['B']:
				col.append(B_label)
			else:
				col.append('Other')
		dataset['sample_metadata']['Group'] = col
		color_by = 'Group'
		color_type = 'categorical'

	# Return
	tsne_results = {'tsne': tsne_dim, 'sample_metadata': dataset['sample_metadata'].loc[expression_dataframe.columns], 'color_by': color_by, 'color_type': color_type, 'nr_genes': nr_genes}
	return tsne_results

#############################################
########## 2. Plot
#############################################

def plot(tsne_results, plot_counter):

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
		marker = dict(size=15, color=color_column, colorscale='Viridis', showscale=True)
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
			trace = go.Scatter3d(x=[tsne[0][x] for x in category_indices],
								 y=[tsne[1][x] for x in category_indices],
								 z=[tsne[2][x] for x in category_indices],
								 mode='markers',
								 hoverinfo='text',
								 text=[sample_titles[x] for x in category_indices],
								 name = category,
								 marker=dict(size=15, color=category_color))
			
			# Append trace to data list
			data.append(trace)
	
	# Prepare figure
	colored = '' if str(color_by) == 'None' else 'Colored by {}'.format(color_by)
	layout = go.Layout(title='<b>t-SNE Analysis | Scatter Plot</b><br><i>{}</i>'.format(colored), hovermode='closest', margin=go.Margin(l=0,r=0,b=0,t=50), width=900,
		scene=dict(xaxis=dict(title='t-SNE1'), yaxis=dict(title='t-SNE2'),zaxis=dict(title='t-SNE3')))
	fig = go.Figure(data=data, layout=layout)

	# Plot
	iplot(fig)

	# Add Figure Legend
	display(Markdown('** Figure '+plot_counter()+' | t-SNE **'.format(**locals())))

