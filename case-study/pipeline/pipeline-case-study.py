#################################################################
#################################################################
############### BioJupies Case Study ################
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
import os
from sqlalchemy import create_engine
import pymysql
import json
import pandas as pd
import scipy.stats as ss
pymysql.install_as_MySQLdb()
# from rpy2.robjects import r, pandas2ri
# pandas2ri.activate()

##### 2. Custom modules #####
# Pipeline running
# sys.path.append('/Users/denis/Documents/Projects/scripts')
# sys.path.append('pipeline/scripts')
# import Support3 as S
# import CaseStudy as P

# Library
version = 'v0.6'
sys.path.append('/Users/denis/Documents/Projects/jupyter-notebook/notebook-generator/library/{}/core_scripts/load'.format(version))
sys.path.append('/Users/denis/Documents/Projects/jupyter-notebook/notebook-generator/library/{}/core_scripts/signature'.format(version))
import load
import signature

#############################################
########## 2. General Setup
#############################################
##### 1. Variables #####

##### 2. R Connection #####

#######################################################
#######################################################
########## S1. Get Signature Metadata
#######################################################
#######################################################

#############################################
########## 1. Download Metadata
#############################################

@follows(mkdir('s1-signature_metadata.dir'))

@files('rawdata/p53_MDM2_p21_RNA.xlsx',
       's1-signature_metadata.dir/signature_metadata.csv')

def processMetadata(infile, outfile):

    # Read
    signature_dataframe = pd.read_excel(infile, index_col='biojupies')

    # Filter
    signature_dataframe = signature_dataframe[['cell_line', 'cell_type', 'pert_type', 'gene_targets']].fillna('')

    # Write
    signature_dataframe.to_csv(outfile)#, sep='\t')

#############################################
########## 1. Split Files
#############################################

@follows(mkdir('s1-signature_metadata.dir/json'))

@subdivide('rawdata/p53_MDM2_p21_RNA.xlsx',
           formatter(),
           's1-signature_metadata.dir/json/*.json',
           's1-signature_metadata.dir/json/')

def splitSignatures(infile, outfile, outfileRoot):

    # Read
    signature_dataframe = pd.read_excel(infile, index_col='biojupies')

    # Loop through rows
    for index, rowData in signature_dataframe.iterrows():
        
        # Check if human
        if rowData['organism'] == 'human' and index not in ['pYOLeicSn']:
            
            # Process metadata
            signature_metadata = {
                'control': rowData['ctrl_ids'].strip().split(' '),
                'perturbation': rowData['pert_ids'].strip().split(' '),
                'gse': rowData['geo_id'],
                'platform': rowData['platform']
            }

            # Get outfile
            outfile = '{outfileRoot}{index}.json'.format(**locals())

            # Write
            with open(outfile, 'w') as openfile:
                openfile.write(json.dumps(signature_metadata, indent=4))

#######################################################
#######################################################
########## S2. Calculate Signatures
#######################################################
#######################################################

#############################################
########## 1. Run Differential Expression
#############################################

@follows(mkdir('s2-signatures.dir'))

@transform(splitSignatures,
           regex(r'.*/(.*).json'),
           r's2-signatures.dir/\1-signature.txt')

def generateSignatures(infile, outfile):

    # Print status
    print('Doing {}...'.format(outfile))

    # Read metadata
    with open(infile) as openfile:
        signature_metadata = json.loads(openfile.read())

    # Load dataset
    dataset = load.archs4(gse=signature_metadata['gse'], platform=signature_metadata['platform'])

    # Calculate signature
    signature_dataframe = signature.cd(dataset=dataset, log=False, group_A=signature_metadata['control'], group_B=signature_metadata['perturbation'])

    # Write
    signature_dataframe.to_csv(outfile, sep='\t')

#######################################################
#######################################################
########## S3. Merge Signatures
#######################################################
#######################################################

#############################################
########## 1. Merge
#############################################

@follows(mkdir('s3-merged.dir'))

@merge(generateSignatures,
       's3-merged.dir/signature-table.txt')

def mergeSignatures(infiles, outfile):

    # Initialize list
    results = []

    # Loop through infiles
    for infile in infiles:

        # Print
        print('Doing {}...'.format(infile))
        
        # Read signature
        try:
            signature_dataframe = pd.read_table(infile)
        except:
            continue
            
        # Add signature label
        signature_dataframe['notebook_uid'] = os.path.basename(infile).split('-')[0]

        # Append
        results.append(signature_dataframe)
        
    # Concatenate and cast
    results_dataframe = pd.concat(results).pivot_table(index='gene_symbol', columns='notebook_uid', values='CD')

    # Save
    results_dataframe.to_csv(outfile, sep='\t')

#######################################################
#######################################################
########## S4. Correlation Analysis
#######################################################
#######################################################

#############################################
########## 1. Calculate Correlation 
#############################################

@follows(mkdir('s4-correlation.dir'))

@files(mergeSignatures,
       's4-correlation.dir/signature-correlation.txt')

def correlateSignatures(infile, outfile):

    # Read
    signature_dataframe = pd.read_table(infile, index_col='gene_symbol')

    # Get top genes
    top_genes = signature_dataframe.var(axis=1).sort_values(ascending=False).index[:5000]

    # Filter
    filtered_signature_dataframe = signature_dataframe.loc[top_genes]#.apply(ss.zscore, axis=1).drop(['Q0FknOiJz'], axis=1)

    # Calculate pairwise correlations
    correlation_dataframe = round(filtered_signature_dataframe.corr(method='spearman'), ndigits=3)
    correlation_dataframe.index.name = 'notebook_uid'

    # Write
    correlation_dataframe.to_csv(outfile, sep='\t')

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
pipeline_run([sys.argv[-1]], multiprocess=5, verbose=1)
print('Done!')
