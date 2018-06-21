#################################################################
#################################################################
############### BioJupies Ontologies ################
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
import sys, os, gzip, glob, json
import pandas as pd
import urllib.request
from io import StringIO

##### 2. Custom modules #####
# Pipeline running

#############################################
########## 2. General Setup
#############################################
##### 1. Variables #####
links = {
    'disease_ontology': {'url': 'http://data.bioontology.org/ontologies/DOID/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv', 'format': 'csv', 'gzip': True},
    'drug_ontology': {'url': 'http://data.bioontology.org/ontologies/DRON/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv', 'format': 'csv', 'gzip': True},
    'human_genes': {'url': 'ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz', 'format': 'txt', 'gzip': True},
    'mouse_genes': {'url': 'ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Mus_musculus.gene_info.gz', 'format': 'txt', 'gzip': True},
    'clo_ontology': {'url': 'http://data.bioontology.org/ontologies/CLO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv', 'format': 'csv', 'gzip': True}
}

##### 2. R Connection #####

#######################################################
#######################################################
########## S1. Download Data
#######################################################
#######################################################

#############################################
########## 1. Download
#############################################

def downloadJobs():
    for key, value in links.items():
        outfile = 's1-rawdata.dir/{key}.{value[format]}'.format(**locals())
        yield (None, outfile)

@follows(mkdir('s1-rawdata.dir'))
@files(downloadJobs)

def downloadFiles(infile, outfile):
    
    # Get file
    source = os.path.basename(outfile).split('.')[0]

    # Read file
    response = urllib.request.urlopen(links[source]['url'])

    # Save to file
    with open(outfile, 'wb') as openfile:
        if links[source]['gzip']:
            openfile.write(gzip.decompress(response.read()))
        else:
            openfile.write(response.read())

#######################################################
#######################################################
########## S2. Process Data
#######################################################
#######################################################

#############################################
########## 1. Disease Ontology
#############################################

@follows(mkdir('s2-processed_data.dir'))

@transform('s1-rawdata.dir/disease_ontology.csv',
           regex(r'.*/(.*).csv'),
           r's2-processed_data.dir/\1-processed.txt')

def processDiseaseOntology(infile, outfile):

    # Read data
    ontology_dataframe = pd.read_csv(infile)

    # Filted and rename
    ontology_dataframe = ontology_dataframe[ontology_dataframe['Obsolete'] == False]
    columns = {'Preferred Label': 'term_name', 'definition': 'term_description', 'Class ID': 'term_id'}
    ontology_dataframe = ontology_dataframe.rename(columns=columns)[list(columns.values())]
    ontology_dataframe['term_id'] = [os.path.basename(x) for x in ontology_dataframe['term_id']]

    # Write
    ontology_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 2. Drug Ontology
#############################################

@transform('s1-rawdata.dir/drug_ontology.csv',
           regex(r'.*/(.*).csv'),
           r's2-processed_data.dir/\1-processed.txt')

def processDrugOntology(infile, outfile):

    # Read data
    ontology_dataframe = pd.read_csv(infile)
 
    # Filter and rename
    ontology_dataframe = ontology_dataframe[[not x.isnumeric() and 'MG' not in x and '/' not in x for x in ontology_dataframe['Preferred Label']]]
    columns = {'Preferred Label': 'term_name', 'definition': 'term_description', 'Class ID': 'term_id'}
    ontology_dataframe = ontology_dataframe.rename(columns=columns)[list(columns.values())]
    ontology_dataframe['term_id'] = [os.path.basename(x) for x in ontology_dataframe['term_id']]

    # Write
    ontology_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 3. Genes
#############################################

@transform(glob.glob('s1-rawdata.dir/*_genes.txt'),
           regex(r'.*/(.*).txt'),
           r's2-processed_data.dir/\1-processed.txt')

def processGenes(infile, outfile):

    # Read data
    ontology_dataframe = pd.read_table(infile)
 
    # Filter and rename
    # ontology_dataframe = ontology_dataframe[[not x.isnumeric() and 'MG' not in x and '/' not in x for x in ontology_dataframe['Preferred Label']]]
    columns = {'Symbol': 'term_name', 'description': 'term_description', 'GeneID': 'term_id'}
    ontology_dataframe = ontology_dataframe.rename(columns=columns)[list(columns.values())]

    # Write
    ontology_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 4. Cell Lines
#############################################

@files('s1-rawdata.dir/clo_ontology.csv',
       's2-processed_data.dir/cell_line_ontology-processed.txt')

def processCellLines(infile, outfile):

    # Read data
    ontology_dataframe = pd.read_csv(infile)
 
    # Filter and rename
    ontology_dataframe = ontology_dataframe[['CLO' in x for x in ontology_dataframe['Class ID']]]
    columns = {'Preferred Label': 'term_name', 'Definitions': 'term_description', 'Class ID': 'term_id'}
    ontology_dataframe = ontology_dataframe.rename(columns=columns)[list(columns.values())]
    ontology_dataframe['term_id'] = [os.path.basename(x) for x in ontology_dataframe['term_id']]
    ontology_dataframe['term_name'] = [x.replace(' cell', '') for x in ontology_dataframe['term_name']]

    # Write
    ontology_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 5. Tissues
#############################################

@files('s1-rawdata.dir/clo_ontology.csv',
       's2-processed_data.dir/anatomy_ontology-processed.txt')

def processTissues(infile, outfile):

    # Read data
    ontology_dataframe = pd.read_csv(infile)
 
    # Filter and rename
    ontology_dataframe = ontology_dataframe[['UBERON' in x for x in ontology_dataframe['Class ID']]]
    columns = {'Preferred Label': 'term_name', 'Definitions': 'term_description', 'Class ID': 'term_id'}
    ontology_dataframe = ontology_dataframe.rename(columns=columns)[list(columns.values())]
    ontology_dataframe['term_id'] = [os.path.basename(x) for x in ontology_dataframe['term_id']]
    # ontology_dataframe['term_name'] = [x.replace(' cell', '') for x in ontology_dataframe['term_name']]

    # Write
    ontology_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 6. Gene Perturbations
#############################################

@files('s1-rawdata.dir/gene_perturbation.json',
       's2-processed_data.dir/gene_perturbation-processed.txt')

def processPerturbations(infile, outfile):

    # Read data
    with open(infile) as openfile:
        ontology_dataframe = pd.DataFrame(json.loads(openfile.read()))
    ontology_dataframe.to_csv(outfile, sep='\t', index=False)

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
