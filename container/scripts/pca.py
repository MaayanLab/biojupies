#######################################################
########## 1. Modules #################################
#######################################################
import sklearn
import numpy as np
import scipy.stats as ss
from sklearn.decomposition import PCA
from plotly.offline import iplot
from plotly.graph_objs import Scatter3d, Layout, Figure

#######################################################
########## 2. Regular Heatmap #########################
#######################################################

def display(dataframe, log=True, normalize_cols=True, filter_rows=True, nr_filtered_rows=500, z_score=True, width=900, height=600):

	# Log
	if log:
		dataframe = np.log10(dataframe+1)
		
	# Normalize
	if normalize_cols:
		dataframe = dataframe/dataframe.sum()
		
	# Filter rows
	if filter_rows:
		top_genes = dataframe.var(axis=1).sort_values(ascending=False).index.tolist()[:nr_filtered_rows]
		dataframe = dataframe.loc[top_genes]
		
	# Z-score
	if z_score:
		dataframe = dataframe.apply(ss.zscore, 1)
		
	# Run PCA
	pca = PCA(n_components=3)
	pca.fit(dataframe)

	# Get variance explained
	var_explained = ['PC'+str((i+1))+'('+str(round(e*100, 1))+'% var. explained)' for i, e in enumerate(pca.explained_variance_ratio_)]

	# Plot
	trace = Scatter3d(
		x=pca.components_[0],
		y=pca.components_[1],
		z=pca.components_[2],
		mode='markers',
		hoverinfo='text',
		text=dataframe.columns,
		marker=dict(
			size=12,
		)
	)

	layout = Layout(
		hovermode='closest',
		width=width,
		height=height,
		scene=dict(
			xaxis=dict(title=var_explained[0]),
			yaxis=dict(title=var_explained[1]),
			zaxis=dict(title=var_explained[2]),
		),
		margin=dict(
			l=0,
			r=0,
			b=0,
			t=0
		)
	)
	fig = Figure(data=[trace], layout=layout)
		
	# Return
	return iplot(fig)