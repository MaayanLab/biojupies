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
import sys, glob, h5py, os, time, urllib.request, json
import pandas as pd
import xml.etree.ElementTree as ET
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

@merge(glob.glob('s1-h5.dir/h5/*.h5'),
	   's2-samples.dir/samples.txt')

def getSamples(infiles, outfile):

	# Loop through infiles
	results = []
	for infile in infiles:
		f = h5py.File(infile, 'r')
		gse, gpl = os.path.basename(infile)[:-len('.h5')].split('-')
		sample_dataframe = pd.DataFrame({x: f['meta']['sample'][x] for x in ['Sample_geo_accession', 'Sample_title']}).rename(columns={'Sample_geo_accession': 'gsm', 'Sample_title': 'sample_title'})
		sample_dataframe['gse'] = gse
		sample_dataframe['gpl'] = gpl
		results.append(sample_dataframe)
	result_dataframe = pd.concat(results)
	result_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 2. Get Dataset Annotations
#############################################

@follows(mkdir('s2-samples.dir/annotations'))

@subdivide(getSamples,
		   formatter(),
		   's2-samples.dir/annotations/*.txt',
		   's2-samples.dir/annotations/')

def getSeriesAnnotations(infile, outfiles, outfile_root):

	# Read infile
	gse_list = pd.read_table(infile)['gse'].unique()

	# Loop through GSE
	for gse in gse_list:
		outfile = '{outfile_root}{gse}-annotation.txt'.format(**locals())
		if not os.path.exists(outfile):
			print('Doing {}'.format(gse))
			try:
				geoId = ET.fromstring(urllib.request.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term={}%5BAccession%20ID%5D'.format(gse)).read()).findall('IdList')[0][0].text
				root = ET.fromstring(urllib.request.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id={geoId}'.format(**locals())).read())
				annotated_dataset = {x.attrib['Name'].replace('PDAT', 'date'): x.text for x in root.find('DocSum') if 'Name' in x.attrib.keys() and x.attrib['Name'] in ['title', 'summary', 'PDAT']}
				print('Done')
			except:
				annotated_dataset = {x: '' for x in ['title', 'summary']}
				print('Error')
			with open(outfile, 'w') as openfile:
				openfile.write(json.dumps(annotated_dataset))

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
	organisms = {'GPL13112': 'Mouse', 'GPL11154': 'Human', 'GPL17021': 'Mouse', 'GPL16791': 'Human', 'GPL18460': 'Human', 'GPL15103': 'Mouse', 'GPL18573': 'Human', 'GPL19057': 'Mouse'}
	platform_df['organism'] = [organisms[gpl] for gpl in platform_df['gpl']]
	platform_df.to_csv(outfile, index=False)

#############################################
########## 2. Series table
#############################################

@files(getSeriesAnnotations,
	   's3-tables.dir/series-table.csv')

def getSeriesTable(infiles, outfile):
	# Get data
	results = {}
	for infile in infiles:
		with open(infile, 'r') as openfile:
			gse = os.path.basename(infile).split('-')[0]
			results[gse] = json.loads(openfile.read())
	result_dataframe = pd.DataFrame(results).T.reset_index().rename(columns={'index': 'gse'})
	result_dataframe['id'] = [x+1 for x in range(len(result_dataframe.index))]
	result_dataframe = result_dataframe[['id', 'gse', 'title', 'summary', 'date']]
	result_dataframe.to_csv(outfile,index=False)

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

#############################################
########## 4. Sample Metadata table
#############################################

@files([getSampleTable, glob.glob('s1-h5.dir/series/*')],
	   's3-tables.dir/sample_metadata-table.csv')

def getSampleMetadataTable(infiles, outfile):
	# Get samples
	sample_dataframe = pd.read_csv(infiles.pop(0)).rename(columns={'id': 'sample_fk'})
	sample_metadata_dataframe = pd.concat([pd.melt(pd.read_table(x).rename(columns={'Unnamed: 0': 'gsm'}), id_vars='gsm').dropna() for x in infiles[0]]).merge(sample_dataframe, on='gsm', how='inner')[['sample_fk', 'variable', 'value']]
	sample_metadata_dataframe['id'] = [x+1 for x in range(len(sample_metadata_dataframe.index))]
	sample_metadata_dataframe.to_csv(outfile,index=False)

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

# @follows(createDb)

# @transform(glob.glob('s3-tables.dir/*-table.*'),
@transform(glob.glob('s3-tables.dir/sample_metadata-table.csv'),
		   regex(r'.*/(.*)-table.*'),
		   r's4-upload.dir/\1-upload.txt')

def uploadTables(infile, outfile):

	# Read table
	print('Uploading {}...'.format(infile))
	df = pd.read_csv(infile)
	table = os.path.basename(infile).split('-')[0]
	engine.execute('SET FOREIGN_KEY_CHECKS = 0;')
	engine.execute('TRUNCATE TABLE {};'.format(table))
	df.to_sql(table, engine, if_exists='append', index=False)
	engine.execute('SET FOREIGN_KEY_CHECKS = 1;')
	os.system('touch {}'.format(outfile))
	time.sleep(3)

##################################################
##################################################
########## Run pipeline
##################################################
##################################################
pipeline_run([sys.argv[-1]], multiprocess=1, verbose=1)#, forcedtorun_tasks=[getSampleMetadataTable]) #forcedtorun_tasks = [up_to_date_task1])
print('Done!')