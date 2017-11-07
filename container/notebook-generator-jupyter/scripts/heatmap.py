#######################################################
########## 1. Modules #################################
#######################################################
import seaborn as sns
import numpy as np

#######################################################
########## 2. Regular Heatmap #########################
#######################################################

def display(dataframe, log=True, normalize_cols=True, filter_rows=True, nr_filtered_rows=500, z_score=0, cmap=sns.color_palette("RdBu_r", 100), correlation=False, correlation_axis=0, correlation_method='spearman'):

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

	# Correlation
	if correlation:
		z_score = None
		if correlation_axis:
			dataframe = dataframe.corr(method=correlation_method)
		else:
			dataframe = dataframe.T.corr(method=correlation_method)

	# Plot
	return sns.clustermap(dataframe, z_score=z_score, cmap=cmap)