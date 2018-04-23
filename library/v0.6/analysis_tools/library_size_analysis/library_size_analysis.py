#################################################################
#################################################################
############### Library Sizes 
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import plotly.graph_objs as go
from plotly.offline import iplot
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

def run(dataset, color_by=None):
 
 	return {'sample_metadata': dataset['sample_metadata'].loc[dataset['rawdata'].columns], 'library_sizes': dataset['rawdata'].sum().sort_values()/10**6, 'color_by': color_by}

#############################################
########## 2. Plot
#############################################

def plot(library_size_results, plot_counter):
	colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928']
	color_by = library_size_results['color_by']
	sample_metadata = library_size_results['sample_metadata']
	if color_by:
		colored_string = '<i>, colored by {}</i>'.format(color_by)
		color_column = sample_metadata[color_by]
		if str(color_column[0]).isnumeric():
			color = sample_metadata[color_by]
		else:
			unique_categories = color_column.unique()
			color_dict = {cat: colors[i] for i, cat in enumerate(unique_categories)}
			color = [color_dict[x] for x in color_column]
	else:
		color = 'rgb(0,119,177)'
		colored_string = ''
	text = ['<b>{}</b><br>'.format(index)+'<br>'.join('<i>{key}</i>: {value}'.format(**locals()) for key, value in rowData.items()) for index, rowData in sample_metadata.iterrows()]
	data = [go.Bar(x=library_size_results['library_sizes'], y=sample_metadata.index, orientation='h', text=text, hoverinfo='text', marker={'color': color})]
	layout = go.Layout(margin={'l': 100, 't': 75, 'r': 0, 'b': 50, 'pad': 5}, title='<b>Library Size Analysis | Bar Plot</b><br><i>Million reads per sample</i>'+colored_string, xaxis={'title': 'Million Reads'})
	fig = go.Figure(data=data, layout=layout)

	# Plot
	iplot(fig)

	# Figure Legend
	display(Markdown('** Figure '+plot_counter()+' | Library Size Analysis results. **The figure contains an interactive bar chart which displays the total number of reads mapped to each RNA-seq sample in the dataset. Additional information for each sample is available by hovering over the bars. If provided, sample groups are indicated using different colors, thus allowing for easier interpretation of the results'.format(**locals())))