#################################################################
#################################################################
############### RNA-seq Signature Benchmarking ################
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
import sys, json, os, pymysql, glob
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from ast import literal_eval as make_tuple
pymysql.install_as_MySQLdb()

##### 2. Custom modules #####
# Pipeline running
version = 'v0.6'
# sys.path.append('/Users/denis/Documents/Projects/scripts')
# sys.path.append('pipeline/scripts')
sys.path.append('/Users/denis/Documents/Projects/jupyter-notebook/notebook-generator/library/{}/core_scripts/load'.format(version))
sys.path.append('/Users/denis/Documents/Projects/jupyter-notebook/notebook-generator/library/{}/core_scripts/signature'.format(version))
# import Support3 as S
# import Benchmarking as P
import load
import signature

#############################################
########## 2. General Setup
#############################################
##### 1. Variables #####

##### 2. R Connection #####

#######################################################
#######################################################
########## S1. Process Metadata
#######################################################
#######################################################

#############################################
########## 1. Prepare JSON
#############################################

@follows(mkdir('s1-signature_metadata.dir'))

@files('rawdata.dir/tf_mining.txt',
       's1-signature_metadata.dir/signature_metadata.json')

def prepareSignatureMetadata(infile, outfile):

    # Read signature dataframe
    signature_dataframe = pd.read_table(infile).replace('ENCODE', np.nan).dropna()

    # Split samples
    for col in ['ctl', 'case']:
        signature_dataframe[col] = [x.split('|') for x in signature_dataframe[col]]
    signature_dataframe.head()

    # Add signature id
    signature_dataframe['signature_id'] = ['SIG'+str(x+1).rjust(5, '0') for x in signature_dataframe.index]

    # Write
    with open(outfile, 'w') as openfile:
        openfile.write(json.dumps(signature_dataframe.to_dict(orient='records'), indent=4))

#############################################
########## 2. Download
#############################################

@files(prepareSignatureMetadata,
       's1-signature_metadata.dir/processed_samples.txt')

def getProcessedSamples(infile, outfile):
    
    # Read metadata
    with open(infile) as openfile:
        signature_metadata = json.loads(openfile.read())

    # Create database engine
    engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])

    # Get list of signature samples
    sample_dataframe = pd.DataFrame([{'signature_id': signature['signature_id'], 'dataset_accession': signature['series'], 'sample_accession': sample, 'group': group.replace('ctl', 'control').replace('case', 'perturbation')} for signature in signature_metadata for group in ['ctl', 'case'] for sample in signature[group]])

    # Get list of processed samples
    archs_dataframe = pd.read_sql_query('SELECT dataset_accession, sample_accession, platform_accession FROM sample_new s LEFT JOIN dataset d ON d.id=s.dataset_fk LEFT JOIN platform_new p ON p.id=s.platform_fk WHERE sample_accession IN ("'+'", "'.join(sample_dataframe['sample_accession'].unique())+'")', engine)

    # Merge dataframes
    merged_dataframe = sample_dataframe.merge(archs_dataframe, on=['dataset_accession', 'sample_accession'])

    # Pivot
    cast_dataframe = merged_dataframe.pivot_table(index=['signature_id', 'dataset_accession', 'platform_accession'], columns='group', values='sample_accession', aggfunc=lambda x: tuple(x)).reset_index()

    # Merge
    result_dataframe = cast_dataframe.merge(pd.DataFrame(signature_metadata)[['signature_id', 'cell_type', 'pert', 'tf']], on='signature_id').dropna()

    # Write
    result_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 3. Build signature JSON
#############################################

@follows(mkdir('s1-signature_metadata.dir/json'))

@subdivide(getProcessedSamples,
           formatter(),
           's1-signature_metadata.dir/json/*.json',
           's1-signature_metadata.dir/json/')

def buildMetadataJson(infile, outfile, outfileRoot):

    # Read dataframe
    metadata_dataframe = pd.read_table(infile, index_col='signature_id')

    # Convert tuples
    for col in ['control', 'perturbation']:
        metadata_dataframe[col] = [list(make_tuple(x)) for x in metadata_dataframe[col]]

    # Loop through signatures
    for index, rowData in metadata_dataframe.iterrows():

        # Create outfile
        outfile = '{outfileRoot}{index}.json'.format(**locals())

        # Write
        with open(outfile, 'w') as openfile:
            openfile.write(json.dumps(rowData.to_dict(), indent=4))

#######################################################
#######################################################
########## S2. Compute Signatures
#######################################################
#######################################################

#############################################
########## 1. Calculate Signatures
#############################################

@follows(mkdir('s2-signatures.dir'))

def signatureJobs():
    json_list = glob.glob('s1-signature_metadata.dir/json/*.json')
    for json_file in json_list:
        for method in ['cd']:
            outdir = 's2-signatures.dir/'+method
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            outfile = os.path.join(outdir, os.path.basename(json_file)[:-len('.json')]+'-'+method+'.txt')
            yield [json_file, outfile]

@files(signatureJobs)

def computeSignatures(infile, outfile):

    # Print
    print('Doing {}...'.format(outfile))

    # Read JSON
    with open(infile) as openfile:
        signature_metadata = json.loads(openfile.read())

    # Read dataset
    dataset = load.h5(path='/Users/denis/Data/biojupies/h5/s3-series_h5.dir/{dataset_accession}-{platform_accession}.h5'.format(**signature_metadata))

    # Compute signature
    method = os.path.basename(outfile).split('-')[-1][:-len('.txt')]
    signature_dataframe = getattr(signature, method)(dataset=dataset, group_A=signature_metadata['control'], group_B=signature_metadata['perturbation'])

    # Write
    signature_dataframe.to_csv(outfile, sep='\t')

##################################################
##################################################
########## Run pipeline
##################################################
##################################################
pipeline_run([sys.argv[-1]], multiprocess=1, verbose=1)
print('Done!')
