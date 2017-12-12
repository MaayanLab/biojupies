#################################################################
#################################################################
############### Pipeline Support
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import seaborn as sns
import matplotlib.pyplot as plt
from plotly import tools
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go
import numpy as np
from sklearn.decomposition import PCA
import scipy.stats as ss
from clustergrammer_widget import *
from rpy2.robjects import r, pandas2ri
import pandas as pd
from IPython.display import display, Markdown
import requests
import urllib.request
import gzip
import numbers

##### 2. Other libraries #####


#######################################################
#######################################################
########## S1. Exploratory Data Analysis
#######################################################
#######################################################

#############################################
########## 0. Fetch Data
#############################################

def fetch_dataset(dataset_accession, platform=None):
 
	# Get Link Dict
	with urllib.request.urlopen("http://amp.pharm.mssm.edu/archs4/search/getGSEmatrix.php?gse={dataset_accession}".format(**locals())) as response:
		link_dict = {x['platform']: x['ziplink'] for x in json.loads(response.read())}

	# Get Link
	if platform:
		link = link_dict[platform]
	else:
		platform = list(link_dict.keys())[0]
		link = list(link_dict.values())[0]

	# Read Data
	response = urllib.request.urlopen(urllib.request.Request(link, headers={"Accept-Encoding": "gzip"}))
	data = gzip.decompress(response.read()).decode('utf-8')

	# Get Raw Counts
	rawcount_dataframe = pd.DataFrame([x.split('\t') for x in data.split('\n')[1:] if '!' not in x]).drop(0)
	rawcount_dataframe = rawcount_dataframe.rename(columns=rawcount_dataframe.iloc[0]).drop(1).set_index('ID_REF').fillna(0).astype('int')

	# Get Sample Metadata
	sample_metadata_dataframe = pd.DataFrame([x.split('\t') for x in data.split('\n')[1:] if any(y in x for y in ['!Sample_geo_accession', '!Sample_title', '!Sample_characteristics_ch1'])]).T
	sample_metadata_dataframe = sample_metadata_dataframe.rename(columns=sample_metadata_dataframe.iloc[0]).drop(0).set_index('!Sample_geo_accession').fillna(0)
	sample_metadata_dataframe['platform'] = platform

	# Return
	return rawcount_dataframe, sample_metadata_dataframe

#############################################
########## 1. Library Sizes
#############################################

def plot_library_sizes(rawcount_dataframe, title='Library Sizes'):
	# Get library sizes
	library_sizes = rawcount_dataframe.sum()/10*6
	sns.barplot(y=library_sizes.index, x=library_sizes, color='blue', orient='h')
	plt.title(title)
	plt.xlabel('Million Reads')

#############################################
########## 2. PCA
#############################################

def plot_pca(expression_dataframe, sample_metadata_dataframe=None, log=True, zscore=True, nr_genes=5000, color_by=None):
	colors = ['red', 'blue', 'orange', 'purple', 'turkey', 'chicken', 'thanksigiving']
	if log:
		expression_dataframe = np.log10(expression_dataframe+1)
	expression_dataframe = expression_dataframe.loc[expression_dataframe.var(axis=1).sort_values(ascending=False).index[:nr_genes]]
	if zscore:
		expression_dataframe = expression_dataframe.apply(ss.zscore, axis=1)

	pca=PCA(n_components=3)
	pca.fit(expression_dataframe)
	var_explained = ['PC'+str((i+1))+'('+str(round(e*100, 1))+'% var. explained)' for i, e in enumerate(pca.explained_variance_ratio_)]

	if not color_by:
		marker = dict(size=15)
		trace = go.Scatter3d(x=pca.components_[0],
							 y=pca.components_[1],
							 z=pca.components_[2],
							 mode='markers',
							 hoverinfo='text',
							 text=expression_dataframe.columns,
							 marker=marker)
		data = [trace]
	elif isinstance(sample_metadata_dataframe[color_by][0], numbers.Number):
		marker = dict(size=15, color=sample_metadata_dataframe[color_by], colorscale="Viridis", showscale=True)
		trace = go.Scatter3d(x=pca.components_[0],
							 y=pca.components_[1],
							 z=pca.components_[2],
							 mode='markers',
							 hoverinfo='text',
							 text=expression_dataframe.columns,
							 marker=marker)
		data = [trace]
	else:
		# Get unique categories
		unique_categories = sample_metadata_dataframe[color_by].unique()

		# Define empty list
		data = []
			
		# Loop through the unique categories
		for i, category in enumerate(unique_categories):

			# Get the color corresponding to the category
			category_color = colors[i]

			# Get the indices of the samples corresponding to the category
			category_indices = [i for i, sample_category in enumerate(sample_metadata_dataframe[color_by]) if sample_category == category]
			
			# Create new trace
			trace = go.Scatter3d(x=pca.components_[0][category_indices],
								 y=pca.components_[1][category_indices],
								 z=pca.components_[2][category_indices],
								 mode='markers',
								 hoverinfo='text',
								 text=expression_dataframe.columns[category_indices],
								 name = category,
								 marker=dict(size=15, color=category_color))
			
			# Append trace to data list
			data.append(trace)
	
	layout = go.Layout(title='<b>PCA Analysis | Scatter Plot</b><br><i>Top {nr_genes} most variable genes</i>'.format(**locals()),
		hovermode='closest',
		scene=dict(xaxis=dict(title=var_explained[0]), yaxis=dict(title=var_explained[1]),zaxis=dict(title=var_explained[2])),
		margin=go.Margin(l=0,r=0,b=0,t=50))
	fig = go.Figure(data=data, layout=layout)

	return iplot(fig)

#############################################
########## 4. Clustermap
#############################################

def plot_clustermap(expression_dataframe, z_score=0, cmap=sns.color_palette("RdBu_r", 500), log=True, filter_genes=True, nr_genes=500):
	if log:
		expression_dataframe = np.log10(expression_dataframe+1)
	if filter_genes:
		expression_dataframe = expression_dataframe.loc[expression_dataframe.var(axis=1).sort_values(ascending=False).index[:nr_genes]]
	sns.clustermap(expression_dataframe, z_score=z_score, cmap=cmap)

#############################################
########## 5. Clustergram
#############################################

def get_clustergrammer_cats(sample_metadata_dataframe):
	return [{'title': index, 'cats': {value: rowData[rowData==value].index.tolist() for value in set(rowData.values)}} for index, rowData in sample_metadata_dataframe.T.iterrows()]

def plot_clustergram(expression_dataframe, sample_metadata_dataframe=None, zscore=True, log=True, nr_genes=500, col_colors=False, color_by=None):
	if log:
		expression_dataframe = np.log10(expression_dataframe+1)
	net = Network(clustergrammer_widget)
	net.load_df(expression_dataframe)
	net.filter_N_top('row', nr_genes, 'var')
	if zscore:
		net.normalize(axis='row', norm_type='zscore', keep_orig=True)
	if col_colors and color_by:
		clustergrammer_cats = get_clustergrammer_cats(sample_metadata_dataframe[list(color_by)])
		net.add_cats(cat_data=clustergrammer_cats, axis='col')
	net.cluster()
	return net.widget()

#############################################
########## 6. 2D Scatter
#############################################

def plot_2D_scatter(x, y, text='', title='', xlab='', ylab='', hoverinfo='text', color='black', colorscale='Blues', size=8, showscale=False, symmetric_x=False, symmetric_y=False, pad=0.5, hline=False, vline=False, return_trace=False):
	range_x = [-max(abs(x))-pad, max(abs(x))+pad]if symmetric_x else []
	range_y = [-max(abs(y))-pad, max(abs(y))+pad]if symmetric_y else []
	trace = go.Scattergl(x=x, y=y, mode='markers', text=text, hoverinfo=hoverinfo, marker={'color': color, 'colorscale': colorscale, 'showscale': showscale, 'size': size})
	if return_trace:
		return trace
	else:
		layout = go.Layout(title=title, xaxis={'title': xlab, 'range': range_x}, yaxis={'title': ylab, 'range': range_y})
		fig = go.Figure(data=[trace], layout=layout)
		return iplot(fig)

#############################################
########## 7. MA Plot
#############################################

def ma_plot(limma_dataframe, color_by_pvalue=False, pvalue_threshold=0.05, colorscale=[[0, 'black'], [0.9, 'black'], [0.9, 'black'], [1.0, 'rgb(204,0,0)']], signature_label='Treated vs Control'):

	# Text Labels
	text = ['<b>'+index+'</b><br>Avg Expression = '+str(round(rowData['AveExpr'], ndigits=2))+'<br>logFC = '+str(round(rowData['logFC'], ndigits=2))+'<br>p = '+'{:.2e}'.format(rowData['P.Value'])+'<br>FDR = '+'{:.2e}'.format(rowData['adj.P.Val']) for index, rowData in limma_dataframe.iterrows()]

	# Color
	color = [int(x<0.05) for x in limma_dataframe['P.Value']] if color_by_pvalue else 'black'
	color_label = ' (p<{pvalue_threshold})'.format(**locals()) if color_by_pvalue else ''

	plot_2D_scatter(x=limma_dataframe['AveExpr'], y=limma_dataframe['logFC'], text=text, color=color, colorscale=colorscale, symmetric_y=True, xlab='Average Expression', ylab='logFC', title='<b>Differential Gene Expression | {signature_label}</b><br><i>Average Expression vs. logFoldChange{color_label}</i>'.format(**locals()))

	nr_genes = "{:,}".format(len(limma_dataframe.index))
	up = len(limma_dataframe[(limma_dataframe['logFC'] > 0) & (limma_dataframe['adj.P.Val'] < 0.05)].index)
	dn = len(limma_dataframe[(limma_dataframe['logFC'] > 0) & (limma_dataframe['adj.P.Val'] < 0.05)].index)
	display(Markdown('**MA Plot | {signature_label} signature.** The differential expression analysis identified *{up} upregulated genes* and *{dn} downregulated genes* out of *{nr_genes}* (q < 0.05).'.format(**locals())))

#############################################
########## 8. Volcano Plot
#############################################

def volcano_plot(limma_dataframe, color_by_expression=False, colorscale='Jet', signature_label='Treated vs Control'):

	# Text Labels
	text = ['<b>'+index+'</b><br>Avg Expression = '+str(round(rowData['AveExpr'], ndigits=2))+'<br>logFC = '+str(round(rowData['logFC'], ndigits=2))+'<br>p = '+'{:.2e}'.format(rowData['P.Value'])+'<br>FDR = '+'{:.2e}'.format(rowData['adj.P.Val']) for index, rowData in limma_dataframe.iterrows()]

	# Color
	color = limma_dataframe['AveExpr'] if color_by_expression else 'black'
	color_label = ' (colored by Average Expression)' if color_by_expression else ''

	plot_2D_scatter(x=limma_dataframe['logFC'], y=-np.log10(limma_dataframe['P.Value']), text=text, color=color, colorscale=colorscale, showscale=True, symmetric_x=True, xlab='logFC', ylab='log10P', title='<b>Differential Gene Expression | {signature_label}</b><br><i>logFC vs. log10P{color_label}</i>'.format(**locals()))
	
	nr_genes = "{:,}".format(len(limma_dataframe.index))
	up = len(limma_dataframe[(limma_dataframe['logFC'] > 0) & (limma_dataframe['adj.P.Val'] < 0.05)].index)
	dn = len(limma_dataframe[(limma_dataframe['logFC'] > 0) & (limma_dataframe['adj.P.Val'] < 0.05)].index)
	display(Markdown('**Volcano Plot | {signature_label} signature.** The differential expression analysis identified *{up} upregulated genes* and *{dn} downregulated genes* out of *{nr_genes}* (q < 0.05).'.format(**locals())))

#######################################################
#######################################################
########## S2. Differential Expression
#######################################################
#######################################################

#############################################
########## 1. Compute Signature
#############################################

def compute_signature(rawcount_dataframe, treated_samples, control_samples, method='limma'):

	# Connect to R
	r.source('/Users/denis/Documents/Projects/scripts/Scripts.R')
	pandas2ri.activate()

	# Create design dict
	sample_dict = {'experimental': treated_samples, 'control': control_samples}

	# Create design dataframe
	design_dataframe = pd.DataFrame({group_label: {sample:int(sample in group_samples) for sample in rawcount_dataframe.columns} for group_label, group_samples in sample_dict.items()})

	# Convert to R
	rawcount_dataframe_r = pandas2ri.py2ri(rawcount_dataframe)
	design_dataframe_r = pandas2ri.py2ri(design_dataframe)

	# Run
	if method == 'CD':
		signature_dataframe_r = r.run_characteristic_direction(rawcount_dataframe_r, design_dataframe_r)
	elif method == 'limma':
		signature_dataframe_r = r.run_limma(rawcount_dataframe_r, design_dataframe_r)
	else:
		raise ValueError('Wrong method supplied.  Must be limma or CD.')

	# Convert to pandas and sort
	signature_dataframe = pandas2ri.ri2py(signature_dataframe_r).sort_values('P.Value')

	# Add
	return signature_dataframe

#############################################
########## 2. Enrichr
#############################################

def get_genesets(signature_dataframe, signature_col, top_n=True, nr_genes=500):
	genesets = {}
	sorted_genes = signature_dataframe.sort_values(signature_col).index
	genesets['upregulated'] = sorted_genes[-500:]
	genesets['downregulated'] = sorted_genes[:500]
	return genesets

def submit_enrichr_geneset(geneset):
	ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/addList'
	genes_str = '\n'.join(geneset)
	payload = {
	'list': (None, genes_str),
	}
	response = requests.post(ENRICHR_URL, files=payload)
	if not response.ok:
		raise Exception('Error analyzing gene list')
	data = json.loads(response.text)
	return data

def get_enrichr_results(user_list_id, gene_set_libraries=['GO_Biological_Process_2017b', 'GO_Cellular_Component_2017b', 'GO_Molecular_Function_2017b'], overlappingGenes=True):
	ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/enrich'
	query_string = '?userListId=%s&backgroundType=%s'
	results = []
	for gene_set_library in gene_set_libraries:
		response = requests.get(
			ENRICHR_URL + query_string % (user_list_id, gene_set_library)
		 )
		if not response.ok:
			raise Exception('Error fetching enrichment results')

		data = json.loads(response.text)
		resultDataframe = pd.DataFrame(data[gene_set_library], columns=['rank', 'term_name', 'pvalue', 'zscore', 'combined_score', 'overlapping_genes', 'FDR', 'old_pvalue', 'old_FDR'])
		selectedColumns = ['term_name','zscore','combined_score','pvalue', 'FDR'] if not overlappingGenes else ['term_name','zscore','combined_score','FDR', 'overlapping_genes']
		resultDataframe = resultDataframe.loc[:,selectedColumns]
		results.append(resultDataframe)
	concatenatedDataframe = pd.concat(results)
	return concatenatedDataframe

def run_enrichr(signature_dataframe, signature_col, signature_label=None):
	genesets = get_genesets(signature_dataframe=signature_dataframe, signature_col=signature_col)
	enrichr_ids = {geneset_label: submit_enrichr_geneset(geneset=geneset) for geneset_label, geneset in genesets.items()}
	results = []
	if signature_label:
		display(Markdown('**{signature_label} signature**:'.format(**locals())))
	for geneset_label, geneset_data in enrichr_ids.items():
		user_list_id = geneset_data['userListId']
		display(Markdown('Enrichment for **{geneset_label} geneset**: https://amp.pharm.mssm.edu/Enrichr/enrich?dataset={user_list_id}'.format(**locals())))
		results_dataframe = get_enrichr_results(user_list_id=user_list_id)
		results_dataframe['geneset'] = geneset_label
		results.append(results_dataframe)
	enrichment_dataframe = pd.concat(results)
	enrichment_dataframe['nr_overlapping_genes'] = [len(x) for x in enrichment_dataframe['overlapping_genes']]
	return enrichment_dataframe

def plot_enrichr_results(enrichment_dataframe, signature_label='Control vs. Treated'):
	
	# Define figure
	fig = tools.make_subplots(rows=1, cols=2, print_grid=False, shared_yaxes=True, subplot_titles=[x.title()+' Genes' for x in enrichment_dataframe['geneset'].unique()])

	# Loop through genesets
	for i, geneset in enumerate(enrichment_dataframe['geneset'].unique()):
		# Get subset
		enrichment_dataframe_subset = enrichment_dataframe[enrichment_dataframe['geneset'] == geneset]

		# Get text
		plot_text = []
		for index, rowData in enrichment_dataframe_subset.iterrows():
			overlapping_genes = ', '.join(rowData['overlapping_genes'][:5]+['...'] if len(rowData['overlapping_genes']) > 5 else rowData['overlapping_genes'])
			text = '<span style="align-text: left !important;"><b>{term_name}</b><br>p = '.format(**rowData)+'{:.2e}'.format(rowData['FDR'])+'<br>FDR = '+'{:.2e}'.format(rowData['FDR'])+'<br>Z-score = '+str(round(rowData['zscore'], ndigits=2))+'<br><i style="margin-top: 5px;">{nr_overlapping_genes} genes</i>'.format(**rowData)+'<br>{overlapping_genes}'.format(**locals())+'</span>'
			plot_text.append(text)

		trace = plot_2D_scatter(x=enrichment_dataframe_subset['nr_overlapping_genes'], y=-np.log10(enrichment_dataframe_subset['FDR']), return_trace=True, text=plot_text, color='red' if geneset == 'upregulated' else 'blue', xlab='# Overlapping Genes', ylab='log10P', title='<b>Enrichr Results | {signature_label}</b><br><i>Overlapping Geneset vs logP</i>, colored by Zscore'.format(**locals()))
		fig.append_trace(trace, 1, i+1)

	# Return figure
	fig['layout'].update(showlegend=False, title='<b>Enrichr Results | {signature_label}</b><br><i>Overlapping genes vs log10P</i>'.format(**locals()))
	fig['layout']['xaxis1'].update(title='# Overlapping Genes')
	fig['layout']['yaxis1'].update(title='log10P')
	fig['layout']['xaxis2'].update(title='# Overlapping Genes')
	iplot(fig)

# display(Markdown('**Plot Settings:**'));
# interact(plot_pca,
#          expression_dataframe=fixed(rawcount_dataframe),
#          sample_metadata_dataframe=fixed(sample_metadata_dataframe),
#          color_by=Dropdown(description='Color by:', options=[None]+sample_metadata_dataframe.columns.tolist()),
#          log=Checkbox(description='Log10 Normalization', value=True),
#          zscore=Checkbox(description='Z-score Normalization', value=True),
#          nr_genes=IntSlider(description='# Genes', value=2500, min=500, max=5000, step=500, continuous_update=False));


# display(Markdown('**Plot Settings:**'));
# interact(plot_clustergram,
#          expression_dataframe=fixed(rawcount_dataframe),
#          sample_metadata_dataframe=fixed(sample_metadata_dataframe),
#          col_colors=Checkbox(description='Column colors', value=False),
#          color_by=SelectMultiple(description='Color by:', options=sample_metadata_dataframe.columns.tolist()),
#          log=Checkbox(description='Log10 Normalization', value=True),
#          zscore=Checkbox(description='Z-score Normalization', value=True),
#          nr_genes=IntSlider(description='# Genes', value=1000, min=50, max=2500, step=50, continuous_update=False));
