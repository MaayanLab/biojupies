#################################################################
#################################################################
############### BioJupies Database Upload ################
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
import sys, glob, os, json
import pandas as pd

##### 2. Custom modules #####
# Pipeline running
sys.path.append('pipeline/scripts')
import Upload as P

#############################################
########## 2. General Setup
#############################################
##### 1. Variables #####
from sqlalchemy import create_engine, MetaData
engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI']+'?charset=utf8')
version = 'v6'

#######################################################
#######################################################
########## S1. Upload dataset JSON files to database
#######################################################
#######################################################

#############################################
########## 1. Create Tables
#############################################

@transform('sql/create_tables.sql',
           suffix('.sql'),
           '.txt')

def createTables(infile, outfile):

    # Read file
    with open(infile) as openfile:
        query = openfile.read().format(**globals()).replace('\n', '')

    # Execute
    for statement in query.split(';'):
        if statement:
            engine.execute(statement)

    # Create outfile
    os.system('touch {}'.format(outfile))

#############################################
########## 2. Upload JSON
#############################################

@follows(mkdir('s1-upload_datasets.dir'))

@transform(glob.glob('to_upload/datasets/*/*.json'),
           regex(r'to_upload/datasets/(.*)/(.*).json'),
           r's1-upload_datasets.dir/\1/\2.txt')

def uploadJson(infile, outfile):

    # Get dataset json
    with open(infile) as openfile:
        dataset = json.loads(openfile.read())
    print('Doing {dataset_accession}'.format(**dataset))

    # Get dataset accession
    dataset_accession = os.path.basename(infile).split('-')[0]

    # Check if dataset exists
    if not P.exists(dataset_accession, version):

        # Upload dataset
        P.upload_dataset(dataset, version)

        # Upload platform
        P.upload_platform(dataset, version)

        # Upload samples
        P.upload_samples(dataset, version)

        # Upload sample metadata
        P.upload_sample_metadata(dataset, version)

    # Create outfile
    # os.system('touch {}'.format(outfile))

#############################################
########## 3. Rename Tables
#############################################

@transform('sql/rename_tables.sql',
           suffix('.sql'),
           '.txt')

def renameTables(infile, outfile):

    # Read file
    with open(infile) as openfile:
        query = openfile.read().format(**globals()).replace('\n', '')

    # Execute
    for statement in query.split(';'):
        if statement:
            engine.execute(statement)

    # Create outfile
    os.system('touch {}'.format(outfile))

#######################################################
#######################################################
########## S2. Upload metadata files to database
#######################################################
#######################################################

#############################################
########## 1. Upload ontologies
#############################################

@follows(mkdir('s2-upload_metadata.dir'))

@transform(glob.glob('to_upload/ontologies/ontologies.json'),
           regex(r'.*/(.*).json'),
           r's2-upload_metadata.dir/\1-upload.txt')

def uploadOntologies(infile, outfile):

    # Read ontologies JSON
    with open(infile) as openfile:
        ontologies = json.loads(openfile.read())

    # Loop through ontologies
    for ontology_string, ontology in ontologies.items():
        ontology.update({'ontology_string': ontology_string})
        P.upload_data(ontology, list(ontology.keys()), 'ontology', reset_counter=True)

#############################################
########## 2. Upload metadata files
#############################################

@transform(glob.glob('to_upload/ontologies/terms/*'),
           regex(r'.*/(.*)-processed.txt'),
           r's2-upload_metadata.dir/\1-upload.txt')

def uploadTerms(infile, outfile):
    
    # Read dataframe
    ontology_dataframe = pd.read_table(infile)

    # Get Ontology FK
    ontology_string = os.path.basename(infile).split('-')[0]
    ontology_fk = pd.read_sql_query('SELECT id FROM ontology WHERE ontology_string = "{}"'.format(ontology_string), engine).iloc[0,0]

    # Add FK
    ontology_dataframe['ontology_fk'] = ontology_fk

    # Upload
    ontology_dataframe.to_sql('ontology_term', engine, if_exists='append', index=False)

    # Create outfile
    os.system('touch '+outfile)

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
pipeline_run([sys.argv[-1]], multiprocess=1, verbose=1, forcedtorun_tasks=[uploadJson])
print('Done!')
