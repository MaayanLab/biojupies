#################################################################
#################################################################
############### BioJupies GTEX Processing ################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#############################################
########## 1. Load libraries
#############################################
##### 1. Python modules #####
from ruffus import *
import sys
import pandas as pd

##### 2. Custom modules #####
# Pipeline running

#############################################
########## 2. General Setup
#############################################
##### 1. Variables #####
expression_file = 'rawdata/GTEx_Analysis_2016-01-15_v7_RNASeQCv1.1.8_gene_reads.gct'
attribute_file = 'rawdata/GTEx_v7_Annotations_SampleAttributesDS.txt'
phenotype_file = 'rawdata/GTEx_v7_Annotations_SubjectPhenotypesDS.txt'
ensembl_file = 'rawdata/mart_export.txt'

##### 2. R Connection #####

#######################################################
#######################################################
########## S1. Filter Data
#######################################################
#######################################################

#############################################
########## 1. Filter Protein Coding Genes
#############################################

@mkdir('s1-filtered_data.dir')

@transform(expression_file,
           regex(r'.*/(.*).gct'),
           add_inputs(ensembl_file),
           r's1-filtered_data.dir/\1_filtered.txt')

def filterGenes(infiles, outfile):

    # Split infiles
    gtex_infile, ensembl_file = infiles

    # Read GTEx data
    expression_dataframe = pd.read_table(gtex_infile, skiprows=2, index_col='Name').rename(columns={'Description': 'gene_symbol'})

    # Read gene types
    gene_dataframe = pd.read_table(ensembl_file, index_col='Gene stable ID version').rename(columns={'Gene type': 'biotype'}).query('biotype == "protein_coding"')

    # Merge dataframes
    merged_dataframe = expression_dataframe.merge(gene_dataframe, left_index=True, right_index=True)

    # Write
    merged_dataframe.to_csv(outfile, sep='\t')

#######################################################
#######################################################
########## S. 
#######################################################
#######################################################

#############################################
########## . 
#############################################


##################################################
##################################################
########## Run pipeline
##################################################
##################################################
pipeline_run([sys.argv[-1]], multiprocess=1, verbose=1)
print('Done!')
