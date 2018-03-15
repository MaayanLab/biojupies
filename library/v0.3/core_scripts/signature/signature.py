#################################################################
#################################################################
############### Generate Signature
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. General support #####
import os
import pandas as pd
from rpy2.robjects import r, pandas2ri
pandas2ri.activate()

##### 2. R #####
r.source(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'signature.R'))

#######################################################
#######################################################
########## S1. Design Matrix
#######################################################
#######################################################

def make_design_matrix(expression_dataframe, group_A, group_B):

	# Sample names
	group_A = [x.replace(':', '.').replace('-', '.') for x in group_A]
	group_B = [x.replace(':', '.').replace('-', '.') for x in group_B]
	expression_dataframe.columns = [x.replace(':', '.').replace('-', '.') for x in expression_dataframe.columns]

	# Get expression dataframe
	expression_dataframe = expression_dataframe[group_B+group_A]

	# Create design dataframe
	sample_dict = {'A': group_B, 'B': group_A}
	design_dataframe = pd.DataFrame({group_label: {sample:int(sample in group_samples) for sample in expression_dataframe.columns} for group_label, group_samples in sample_dict.items()})

	# Return
	return {'expression': expression_dataframe, 'design': design_dataframe}


#######################################################
#######################################################
########## S2. Signature Generation
#######################################################
#######################################################

#############################################
########## 1. limma
#############################################

def limma(dataset, group_A, group_B):

	# Get design
	processed_data = make_design_matrix(dataset['rawdata'].copy(), group_A, group_B)

	# Add
	return pandas2ri.ri2py(r.limma(pandas2ri.py2ri(processed_data['expression']), pandas2ri.py2ri(processed_data['design']))).sort_values('logFC', ascending=False).set_index('gene_symbol')

#############################################
########## 2. CD
#############################################

def cd(dataset, group_A, group_B, normalization='rawdata', log=False):

	# Get design
	processed_data = make_design_matrix(dataset[normalization].copy(), group_A, group_B)

	# Add
	return pandas2ri.ri2py(r.cd(pandas2ri.py2ri(processed_data['expression']), pandas2ri.py2ri(processed_data['design']), log)).sort_values('CD', ascending=False).set_index('gene_symbol')
