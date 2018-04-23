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

def run(dataset, normalization='logCPM', nr_genes=2500, z_score=True, color_by='auto', color_type='categorical'):

	# Get data
	expression_dataframe = dataset[normalization].copy()
	
	# Filter
	expression_dataframe = expression_dataframe.loc[expression_dataframe.var(axis=1).sort_values(ascending=False).index[:nr_genes]]

	# Z-score
	if z_score == 'True' or z_score == True:
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			expression_dataframe = expression_dataframe.apply(ss.zscore, axis=1)

	# Run PCA
	pca=PCA(n_components=3)
	pca.fit(expression_dataframe)

	# Get Variance
	var_explained = ['PC'+str((i+1))+'('+str(round(e*100, 1))+'% var. explained)' for i, e in enumerate(pca.explained_variance_ratio_)]

	# Estimate colors
	if color_by == 'auto':

		# Add signature groups
		if dataset.get('signature_metadata'):
			A_label, B_label = list(dataset.get('signature_metadata').keys())[0].split(' vs ')
			col = []
			group_dict = list(dataset.get('signature_metadata').values())[0]
			for gsm in dataset['sample_metadata'].index:
				if gsm in group_dict['A']:
					col.append(A_label)
				elif gsm in group_dict['B']:
					col.append(B_label)
				else:
					col.append('Other')
			dataset['sample_metadata']['Sample Group'] = col
			color_by = 'Sample Group'
		else:

			# Add group column, if available
			if 'Group' in dataset['sample_metadata'].columns:
				color_by = 'Group'
			else:
				color_by = None


	# Return
	pca_results = {'pca': pca, 'var_explained': var_explained, 'sample_metadata': dataset['sample_metadata'].loc[expression_dataframe.columns], 'color_by': color_by, 'color_type': color_type, 'nr_genes': nr_genes, 'normalization': normalization, 'signature_metadata': dataset.get('signature_metadata')}
	return pca_results

#############################################
########## 2. Plot
#############################################

def plot(pca_results, plot_counter):

	# Get results
	pca = pca_results['pca']
	var_explained = pca_results['var_explained']
	sample_metadata = pca_results['sample_metadata']
	color_by = pca_results.get('color_by')
	color_type = pca_results.get('color_type')
	color_column = pca_results['sample_metadata'][color_by] if color_by else None
	colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928']
	sample_titles = ['<b>{}</b><br>'.format(index)+'<br>'.join('<i>{key}</i>: {value}'.format(**locals()) for key, value in rowData.items()) for index, rowData in sample_metadata.iterrows()]

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
		marker = dict(size=15, color=color_column, colorscale='Viridis', showscale=True)
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

			# If signature
			if color_by == 'Sample Group':
				group_A, group_B = [x.split(' vs ') for x in pca_results['signature_metadata'].keys()][0]
				if category == group_A:
					category_color = 'blue'
				elif category == group_B:
					category_color = 'red'
				else:
					category_color = 'black'
			else:
				category_color = colors[i]

			# Get the indices of the samples corresponding to the category
			category_indices = [i for i, sample_category in enumerate(color_column) if sample_category == category]
			
			# Create new trace
			trace = go.Scatter3d(x=pca.components_[0][category_indices],
								 y=pca.components_[1][category_indices],
								 z=pca.components_[2][category_indices],
								 mode='markers',
								 hoverinfo='text',
								 text=[sample_titles[x] for x in category_indices],
								 name = category,
								 marker=dict(size=15, color=category_color))
			
			# Append trace to data list
			data.append(trace)
	
	colored = '' if str(color_by) == 'None' else 'Colored by {}'.format(color_by)
	layout = go.Layout(title='<b>PCA Analysis | Scatter Plot</b><br><i>{}</i>'.format(colored), hovermode='closest', margin=go.Margin(l=0,r=0,b=0,t=50), width=900,
		scene=dict(xaxis=dict(title=var_explained[0]), yaxis=dict(title=var_explained[1]),zaxis=dict(title=var_explained[2])))
	fig = go.Figure(data=data, layout=layout)

	# Plot
	iplot(fig)

	# Add Figure Legend
	display(Markdown('** Figure '+plot_counter()+' | Principal Component Analysis results. ** The figure displays an interactive, three-dimensional scatter plot of the first three Principal Components (PCs) of the data. Each point represents an RNA-seq sample. Samples with similar gene expression profiles are closer in the three-dimensional space. If provided, sample groups are indicated using different colors, allowing for easier interpretation of the results.'.format(**locals())))

