#################################################################
#################################################################
############### BioJupies Database Upload - Python Support ############
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#############################################
########## 1. Load libraries
#############################################
##### 1. Python modules #####
import os, pymysql
import pandas as pd
from sqlalchemy import create_engine, MetaData, and_
from sqlalchemy.orm import sessionmaker
pymysql.install_as_MySQLdb()

##### 2. Custom modules #####
# Pipeline running

#############################################
########## 2. General Setup
#############################################
##### 1. Variables #####
# Database engine
engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI']+'?charset=utf8')
Session = sessionmaker(bind=engine)
metadata = MetaData()
metadata.reflect(bind=engine)
tables = metadata.tables

# Dict to statement
def upload_data(data, keys, table, reset_counter=True):
    rowid = engine.execute(tables[table].insert({x: data.get(x) for x in keys}).prefix_with('IGNORE')).lastrowid
    if reset_counter:
        engine.execute('ALTER TABLE {} AUTO_INCREMENT = 1;'.format(table))
    return rowid

#######################################################
#######################################################
########## S1. Upload to Database
#######################################################
#######################################################

#############################################
########## 1. Check if dataset exists
#############################################

def exists(accession, version):
    table = 'dataset_{version}'.format(version=version)
    assert table in tables, 'Invalid table'
    return len(pd.read_sql_query('SELECT * FROM {table} WHERE dataset_accession = %s'.format(table=table), engine, params=(accession,)).index)

#############################################
########## 2. Upload dataset
#############################################

def upload_dataset(dataset, version):

    dataset_types = {'rnaseq': 1, 'microarray': 2}
    dataset.update({'dataset_type_fk': dataset_types[dataset['type']]})
    dataset['dataset_id'] = upload_data(data=dataset, keys=['dataset_title', 'dataset_accession', 'summary', 'date', 'dataset_type_fk'], table='dataset_'+version)

#############################################
########## 3. Upload platform
#############################################

def upload_platform(dataset, version):

    upload_data(data=dataset, keys=['platform_accession'], table='platform_'+version)
    dataset['platform_id'] = engine.execute(tables['platform_'+version].select().where(tables['platform_'+version].columns['platform_accession'] == dataset['platform_accession'])).fetchall()[0]['id']

#############################################
########## 4. Upload samples
#############################################

def upload_samples(dataset, version):

    # Create sample dataframe
    sample_dataframe = pd.DataFrame(dataset['samples']).T.rename(columns={'index': 'Index'}).reset_index().rename(columns={'index': 'sample_accession', 'Sample Title': 'sample_title'})[['sample_accession', 'sample_title']]

    # Add foreign keys
    sample_dataframe['dataset_fk'] = dataset['dataset_id']
    sample_dataframe['platform_fk'] = dataset['platform_id']

    # Upload
    sample_dataframe.to_sql('sample_'+version, engine, if_exists='append', index=False)

    # Get IDs
    dataset['sample_ids'] = pd.DataFrame(engine.execute(tables['sample_'+version].select().where(and_(tables['sample_'+version].columns['sample_accession'].in_(sample_dataframe['sample_accession']), tables['sample_'+version].columns['dataset_fk'] == dataset['dataset_id'], tables['sample_'+version].columns['platform_fk'] == dataset['platform_id']))).fetchall()).rename(columns={0: 'sample_fk', 1: 'sample_accession'})[['sample_fk', 'sample_accession']]

#############################################
########## 4. Upload sample metadata
#############################################

def upload_sample_metadata(dataset, version):

    # Create metadata dataframe
    sample_metadata_dataframe = pd.melt(pd.DataFrame(dataset['samples']).T.reset_index(), id_vars='index').merge(dataset['sample_ids'], left_on='index', right_on='sample_accession')[['sample_fk', 'variable', 'value']]

    # Upload
    sample_metadata_dataframe.to_sql('sample_metadata_'+version, engine, if_exists='append', index=False)

#######################################################
#######################################################
########## S. 
#######################################################
#######################################################

#############################################
########## . 
#############################################
