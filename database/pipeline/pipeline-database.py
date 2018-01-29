#################################################################
#################################################################
############### Notebook Generator Database ################
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
import sys, glob, h5py, os, time
import pandas as pd
from rpy2.robjects import r, pandas2ri
pandas2ri.activate()

##### 2. Custom modules #####
# Pipeline running
sys.path.append('/Users/denis/Documents/Projects/scripts')
sys.path.append('pipeline/scripts')
import Support3 as S
import Database as P

#############################################
########## 2. General Setup
#############################################
##### 1. Variables #####
engine = S.get_engine(db='notebook_generator')

##### 2. R Connection #####
r.source('pipeline/scripts/database.R')

#######################################################
#######################################################
########## S1. Samples
#######################################################
#######################################################

#############################################
########## 1. Get Samples
#############################################

@follows(mkdir('s2-samples.dir'))

@merge(glob.glob('s1-h5.dir/*.h5'),
	   's2-samples.dir/samples.txt')

def getSamples(infiles, outfile):

	# Loop through infiles
	results = []
	for infile in infiles:
		h5 = h5py.File(infile, 'r')
		h5_data = {x:[y.decode('utf-8') for y in h5['meta/'+x].value] for x in ['Sample_title', 'Sample_series_id', 'Sample_geo_accession', 'Sample_platform_id']}#, 'Sample_characteristics_ch1', 'Sample_organism_ch1', 'Sample_source_name_ch1']
		h5_df = pd.DataFrame(h5_data).rename(columns={'Sample_title': 'sample_title', 'Sample_series_id': 'gse', 'Sample_geo_accession': 'gsm', 'Sample_platform_id': 'gpl'})
		results.append(h5_df)
	result_df = pd.concat(results).sort_values(['gse', 'gpl'])
	result_df.to_csv(outfile, sep='\t', index=False)

#######################################################
#######################################################
########## S2. Tables
#######################################################
#######################################################

#############################################
########## 1. Platform table
#############################################

@follows(mkdir('s3-tables.dir'))

@files(getSamples,
	   's3-tables.dir/platform-table.csv')

def getPlatformTable(infile, outfile):
	# Get samples
	platform_df = pd.read_table(infile).drop_duplicates('gpl')
	platform_df['id'] = [x+1 for x in range(len(platform_df.index))]
	platform_df = platform_df[['id', 'gpl']]
	platform_df.to_csv(outfile, index=False)

#############################################
########## 2. Series table
#############################################

@files(getSamples,
	   's3-tables.dir/series-table.csv')

def getSeriesTable(infile, outfile):
	# Get samples
	series_df = pd.read_table(infile).drop_duplicates('gse')
	series_df['id'] = [x+1 for x in range(len(series_df.index))]
	series_df = series_df[['id', 'gse']]
	series_df['gse'] = [x.replace('\t', ';').replace(',', ';').replace('"', '') for x in series_df['gse']]
	series_df.to_csv(outfile, index=False)

#############################################
########## 3. Sample table
#############################################

@files((getSamples, getPlatformTable, getSeriesTable),
	   's3-tables.dir/sample-table.csv')

def getSampleTable(infiles, outfile):
	# Get samples
	files = {}
	files['sample'], files['platform'], files['series'] = infiles
	df = {key: pd.read_table(value) if key == 'sample' else pd.read_csv(value).rename(columns={'id': key+'_fk'}) for key, value in files.items()}
	sample_df = df['sample'].merge(df['platform'], on='gpl', how='inner').merge(df['series'], on='gse', how='inner')[['gsm', 'platform_fk', 'series_fk', 'sample_title']]
	sample_df['id'] = [x+1 for x in range(len(sample_df.index))]
	sample_df.to_csv(outfile,index=False)

#######################################################
#######################################################
########## S3. Upload
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################

@follows(mkdir('s4-upload.dir'))

@files('sql/notebook_generator.sql',
	   's4-upload.dir/db-upload.txt')

def createDb(infile, outfile):

	# Read sql
	with open(infile) as openfile:
		sql = openfile.read()
	engine.execute(sql)
	os.system('touch {outfile}'.format(**locals()))

#############################################
########## 1. Upload Tables
#############################################

@follows(createDb)

@transform(glob.glob('s3-tables.dir/*-table.csv'),
		   regex(r'.*/(.*)-table.csv'),
		   r's4-upload.dir/\1-upload.txt')

def uploadTables(infile, outfile):

	# Read table
	print('Uploading {}...'.format(infile))
	df = pd.read_csv(infile)
	table = os.path.basename(infile).split('-')[0]
	engine.execute('SET FOREIGN_KEY_CHECKS = 0;')
	df.to_sql(table, engine, if_exists='append', index=False)
	engine.execute('SET FOREIGN_KEY_CHECKS = 1;')
	os.system('touch {}'.format(outfile))
	time.sleep(3)

##################################################
##################################################
########## Run pipeline
##################################################
##################################################
pipeline_run([sys.argv[-1]], multiprocess=1, verbose=1)
print('Done!')