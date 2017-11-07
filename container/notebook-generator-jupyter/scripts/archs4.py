#######################################################
########## 1. Modules #################################
#######################################################
import urllib.request
import gzip
import json
import pandas as pd
import numpy as np
import scipy.stats as ss

#######################################################
########## 2. Fetch Dataset ###########################
#######################################################

def fetch_dataset(dataset_accession, platform=None):

    # Get Link Dict
    with urllib.request.urlopen("http://amp.pharm.mssm.edu/archs4/search/getGSEmatrix.php?gse={dataset_accession}".format(**locals())) as response:
        link_dict = {x['platform']: x['ziplink'] for x in json.loads(response.read())}

    # Get Link
    if platform:
        link = link_dict[platform]
    else:
        platform = list(link_dict.keys())[0]
        link = list(link_dict.values())[0]

    # Read Data
    response = urllib.request.urlopen(urllib.request.Request(link, headers={"Accept-Encoding": "gzip"}))
    data = gzip.decompress(response.read()).decode('utf-8')

    # Get Raw Counts
    rawcount_dataframe = pd.DataFrame([x.split('\t') for x in data.split('\n')[1:] if '!' not in x]).drop(0)
    rawcount_dataframe = rawcount_dataframe.rename(columns=rawcount_dataframe.iloc[0]).drop(1).set_index('ID_REF').fillna(0).astype('int')

    # Get Sample Metadata
    sample_metadata_dataframe = pd.DataFrame([x.split('\t') for x in data.split('\n')[1:] if any(y in x for y in ['!Sample_geo_accession', '!Sample_title', '!Sample_characteristics_ch1'])]).T
    sample_metadata_dataframe = sample_metadata_dataframe.rename(columns=sample_metadata_dataframe.iloc[0]).drop(0).set_index('!Sample_geo_accession').fillna(0)
    sample_metadata_dataframe['platform'] = platform

    # Return
    return rawcount_dataframe, sample_metadata_dataframe

#######################################################
########## 3. Normalize Dataset #######################
#######################################################

def normalize_dataset(rawcount_dataframe, method='zscore'):

    # Z-score
    if method == 'zscore':
        norm_dataframe = (rawcount_dataframe/rawcount_dataframe.apply(np.sum, 0)).apply(ss.zscore, 1).dropna()

    # Return
    return norm_dataframe