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
import sys, h5py, os, pymysql
import pandas as pd
from sqlalchemy import create_engine
pymysql.install_as_MySQLdb()

##### 2. Custom modules #####
# Pipeline running

#############################################
########## 2. General Setup
#############################################
##### 1. Variables #####
expression_file = 'rawdata/GTEx_Analysis_2016-01-15_v7_RNASeQCv1.1.8_gene_reads.gct'
attribute_file = 'rawdata/GTEx_v7_Annotations_SampleAttributesDS.txt'
phenotype_file = 'rawdata/GTEx_v7_Annotations_SubjectPhenotypesDS.txt'
ensembl_file = 'rawdata/mart_export_names.txt'

##### 2. R Connection #####

#######################################################
#######################################################
########## S1. Filter Data
#######################################################
#######################################################

#############################################
########## 1. Filter Metadata
#############################################

@mkdir('s1-filtered_data.dir')

@transform(attribute_file,
           regex(r'.*/(.*)_SampleAttributesDS.txt'),
           add_inputs(phenotype_file),
           r's1-filtered_data.dir/\1_metadata.txt')

def filterMetadata(infiles, outfile):

    # Split infiles
    attribute_file, phenotype_file = infiles

    # Read data
    attribute_dataframe = pd.read_table(attribute_file)
    phenotype_dataframe = pd.read_table(phenotype_file)

    # Add SUBJID to attribute dataframe
    attribute_dataframe['SUBJID'] = ['-'.join(x.split('-')[:2]) for x in attribute_dataframe['SAMPID']]

    # Merge dataframes
    merged_dataframe = attribute_dataframe.merge(phenotype_dataframe, on='SUBJID')

    # Write
    merged_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 2. Convert to feather
#############################################

@transform(expression_file,
           suffix('.gct'),
           '.feather')

def featherData(infile, outfile):

    # Read dataframe
    print('Reading data...')
    expression_dataframe = pd.read_table(infile, skiprows=2)

    # Write feather
    print('Writing data...')
    expression_dataframe.to_feather(outfile)
            
#############################################
########## 3. Filter Protein Coding Genes
#############################################

@transform(featherData,
           regex(r'.*/(.*).feather'),
           add_inputs(ensembl_file),
           r's1-filtered_data.dir/\1_filtered.feather')

def filterGenes(infiles, outfile):

    # Split infiles
    gtex_infile, ensembl_file = infiles

    # Read GTEx data
    print('Reading data...')
    expression_dataframe = pd.read_feather(gtex_infile).set_index('Description').drop('Name', axis=1)

    # Read gene types
    print('Doing other stuff...')
    gene_dataframe = pd.read_table(ensembl_file, index_col='Gene name').rename(columns={'Gene type': 'biotype'}).query('biotype == "protein_coding"')

    # Merge dataframes
    merged_dataframe = expression_dataframe.merge(gene_dataframe, left_index=True, right_index=True).drop('biotype', axis=1).rename_axis('gene_symbol').reset_index()

    # Write
    merged_dataframe.to_feather(outfile)

#######################################################
#######################################################
########## S2. Build HDF5
#######################################################
#######################################################

#############################################
########## 1. Build H5
#############################################

@follows(mkdir('s2-h5.dir'))
@merge(('s1-filtered_data.dir/GTEx_Analysis_2016-01-15_v7_RNASeQCv1.1.8_gene_reads_filtered.feather', filterMetadata),
       # @merge((filterGenes, filterMetadata),
       's2-h5.dir/gtex_counts.h5')

def buildHDF5(infiles, outfile):

    # Split infiles
    data_file, metadata_file = infiles

    # Read files
    expression_dataframe = pd.read_feather(data_file).set_index('gene_symbol')
    metadata_dataframe = pd.read_table(metadata_file).set_index('SAMPID', drop=False)

    # Get common samples
    common_samples = set(expression_dataframe.columns).intersection(set(metadata_dataframe.index))
    expression_dataframe = expression_dataframe.reindex(common_samples, axis=1)
    metadata_dataframe = metadata_dataframe.reindex(common_samples)

    # Create HDF5
    f = h5py.File(outfile, 'w')

    # Create data
    data_grp = f.create_group('data')
    data_grp.create_dataset('expression', expression_dataframe.shape, data=expression_dataframe.values, chunks=True, dtype=int, compression="gzip")

    # Metadata
    gene_grp = f.create_group('meta/gene')
    gene_grp.create_dataset('symbol', data=expression_dataframe.index, dtype=h5py.special_dtype(vlen=str))

    # Add sample title and accession
    sample_metadata_grp = f.create_group('meta/sample')
    # for col in metadata_dataframe.columns:
    for col in ['SAMPID', 'SMTS', 'SMTSD', 'AGE', 'SEX', 'SMNABTCH']:
        sample_metadata_grp.create_dataset(col, data=metadata_dataframe[col].astype(str), dtype=h5py.special_dtype(vlen=str))

    # Close file
    f.close()

#############################################
########## 2. Get metadata
#############################################

@transform(buildHDF5,
           suffix('_counts.h5'),
           '_metadata.txt')

def getMetadata(infile, outfile):

    # Read H5
    f = h5py.File(infile, 'r')

    # Get metadata
    metadata_dataframe = pd.DataFrame({x: f['meta']['sample'][x].value for x in f['meta']['sample'].keys()})

    # Create engine
    engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])

    # Upload
    metadata_dataframe.to_sql('gtex_metadata', engine)

    # Write
    os.system('touch '+outfile)

##################################################
##################################################
########## Run pipeline
##################################################
##################################################
pipeline_run([sys.argv[-1]], multiprocess=1, verbose=1)
print('Done!')
