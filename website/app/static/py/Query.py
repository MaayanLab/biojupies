#################################################################
#################################################################
############### Query API #######################################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#################################################################
#################################################################
############### 1. Library Configuration ########################
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. Python modules #####
import pandas as pd
from sqlalchemy import  or_, and_, func
import urllib.request
from bs4 import BeautifulSoup

#############################################
########## 2. Variables
#############################################

#################################################################
#################################################################
############### 1. Search Datasets ##############################
#################################################################
#################################################################

#############################################
########## 1. Search GEO
#############################################

def searchGEO(q):

    # Try
    try:

        # Encode query
        q = urllib.request.quote(q)

        # Search
        esearch = BeautifulSoup(urllib.request.urlopen('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term={}%20AND%20Expression%20profiling%20by%20high%20throughput%20sequencing[Filter]'.format(q)).read().decode('utf-8'), 'lxml')

        # Get IDs
        ids = ','.join([x.text for x in esearch.find_all('id')])

        # Summary
        esummary = BeautifulSoup(urllib.request.urlopen('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id={}'.format(ids)).read().decode('utf-8'), 'lxml')

        # Get accessions
        accessions = [x.text for x in esummary.find_all('item', {'name': 'Accession'}) if not x.text.startswith('GSM')]

    # Except
    except:

        # Empty list
        accessions = []

    # Return
    return accessions
#############################################
########## 2. Search Database
#############################################

def searchDatasets(session, tables, min_samples, max_samples, organisms, sortby='asc', q=None):

    # Build database query
    nr_samples_label = func.count(tables['sample_v6'].columns['sample_accession']).label('nr_samples')
    db_query = session.query(tables['dataset_v6'], tables['platform_v6'], nr_samples_label) \
                    .join(tables['sample_v6'], tables['sample_v6'].columns['dataset_fk'] == tables['dataset_v6'].columns['id']) \
                    .join(tables['platform_v6'], tables['platform_v6'].columns['id'] == tables['sample_v6'].columns['platform_fk'])

    # Add filters
    if q:
        db_query = db_query.filter(or_( \
                        tables['dataset_v6'].columns['dataset_title'].like('% '+q+' %'), \
                        tables['dataset_v6'].columns['summary'].like('% '+q+' %'), \
                        tables['dataset_v6'].columns['dataset_accession'].like(q), \
                        tables['dataset_v6'].columns['dataset_accession'].in_(searchGEO(q))
                    ))

    # Group query
    db_query = db_query.group_by(tables['dataset_v6'].columns['dataset_accession']) \
                .having(and_( \
                    tables['platform_v6'].columns['organism'].in_(organisms), \
                    nr_samples_label >= min_samples,
                    nr_samples_label <= max_samples
                ))

    # Sort query results
    if sortby == 'asc':
        db_query = db_query.order_by(func.count(tables['sample_v6'].columns['sample_accession']).asc())
    elif sortby == 'desc':
        db_query = db_query.order_by(func.count(tables['sample_v6'].columns['sample_accession']).desc())
    elif sortby == 'new':
        db_query = db_query.order_by(tables['dataset_v6'].columns['date'].desc())

    # Finish query
    query_dataframe = pd.DataFrame(db_query.all())

    # Add query
    if q:
        session.execute(tables['search'].insert({'query': q}))
        session.commit()

    # Close session
    session.close()

    # Return 
    return query_dataframe
