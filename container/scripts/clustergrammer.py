#######################################################
########## 1. Modules #################################
#######################################################
from clustergrammer_widget import *

#######################################################
########## 2. Fetch Dataset ###########################
#######################################################

def display_clustergram(dataframe, filter_rows=True, filter_rows_by='var', filter_rows_n=500):

    net = Network(clustergrammer_widget)
    net.load_df(dataframe)
    if filter_rows:
        net.filter_N_top('row', filter_rows_n, filter_rows_by)
    net.cluster()
    return net.widget()