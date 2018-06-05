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
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

##### 2. Other libraries #####
from IPython.display import display, Markdown

#######################################################
#######################################################
########## S1. Function
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

def run(datasets, gene_symbols, signatures):

	return {'datasets': datasets, 'gene_symbols': gene_symbols, 'signatures': signatures}


#############################################
########## 2. Plot
#############################################

def plot(results, plot_counter, order=None):

	# Loop through genes 
	for geneset_label, gene_symbols in results['gene_symbols'].items():
		display(Markdown('### '+geneset_label))
		for gene_symbol in list(gene_symbols):

			# Plot
			fig, axes = plt.subplots(ncols=2, figsize=(8.5, 4), sharey=True)
			fig.tight_layout()
			for i, dataset in enumerate(results['datasets']):

				# Normalize
				normdata = np.log10(dataset['data']['rawdata']/dataset['data']['rawdata'].sum()*10**6+1)

				# Get group dataframe
				group_dataframe = pd.DataFrame([{'Group': group, 'sample': sample} for group, samples in dataset['groups'].items() for sample in samples]).set_index('sample')

				# Get plot dataframe
				plot_dataframe = normdata.loc[gene_symbol].rename('logCPM').to_frame().merge(group_dataframe, left_index=True, right_index=True)

				# Add label
				plot_dataframe['dataset'] = dataset['label']

				# Order
				order = ('Control', 'ALOall', 'OIOall') if 'Control' in group_dataframe['Group'].unique() else ('WT', 'LepDBWR', 'LepDB')

				# Plot
				ax = sns.boxplot(x='Group', y='logCPM', data=plot_dataframe, ax=axes[i], order=order)
				ax.set(xlabel='', ylabel='Gene Expression (logCPM)' if not i else '', title='logFC={logFC:.2f}, P-value={FDR:.2e}'.format(**results['signatures'][dataset['label']].rename(columns={'adj.P.Val': 'FDR'}).loc[gene_symbol]))
				ax.set(xlabel='', ylabel='Gene Expression (logCPM)' if not i else '')
			plt.suptitle(gene_symbol+' | Gene Expression', fontsize=17)
			fig.subplots_adjust(top=0.82)
			plt.show()
			gene_symbol_upper = gene_symbol.upper() # add ARCHS4
			display(Markdown('**{gene_symbol}**: [MGI](http://www.informatics.jax.org/searchtool/Search.do?query={gene_symbol}), [Harmonizome](http://amp.pharm.mssm.edu/Harmonizome/gene/{gene_symbol_upper}), [ARCHS4](https://amp.pharm.mssm.edu/archs4/search/genepage.php?gene={gene_symbol_upper})'.format(**locals())))
			display(Markdown(''))
				# g.set_axis_labels("", "logCPM").set_titles("{gene_symbol}".format(**locals()));


