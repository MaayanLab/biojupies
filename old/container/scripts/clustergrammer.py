#######################################################
########## 1. Modules #################################
#######################################################
from clustergrammer_widget import *
import numpy as np

#######################################################
########## 2. Fetch Dataset ###########################
#######################################################

def display_clustergram(dataframe, log=True, normalize_cols=True, filter_rows=True, filter_rows_by='var', filter_rows_n=500, normalize=True):

    # Log
    if log:
        dataframe = np.log10(dataframe+1)
        
    # Normalize
    if normalize_cols:
        dataframe = dataframe/dataframe.sum()

    net = Network(clustergrammer_widget)
    net.load_df(dataframe)
    if filter_rows:
        net.filter_N_top('row', filter_rows_n, filter_rows_by)
    if normalize:
        net.normalize()
    net.cluster()
    return net.widget()