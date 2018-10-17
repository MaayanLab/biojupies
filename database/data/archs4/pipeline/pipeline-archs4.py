#################################################################
#################################################################
############### ARCHS4 Data Packaging ################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

###### TO RUN:
### 1. Create a new folder (e.g. v7) in rawdata.dir and place new H5 files
### 2. Create a new folder s4-series_h5.dir and symlink to a folder not on cloud storage to store H5 packages
### 3. Replace new version in uploadData function
### 4. Remove folders s1, s5, s6
### 5. Run pipeline
### In the future, automate this.

#############################################
########## 1. Load libraries
#############################################
##### 1. Python modules #####
from ruffus import *
import sys, glob, h5py, os, time, urllib, gzip, json
import pandas as pd
import xml.etree.ElementTree as ET
from google.cloud import storage

##### 2. Custom modules #####
# Pipeline running
sys.path.append('/Users/denis/Documents/Projects/scripts')
import Support3 as S

#############################################
########## 2. General Setup
#############################################
##### 1. Variables #####
h5_files = glob.glob('rawdata.dir/v6/*.h5')

#######################################################
#######################################################
########## S1. Download Data from GEO
#######################################################
#######################################################

### add a step where you go from ARCHS4 H5 file to a table containing the following columns: | gse | gpl | comma-separated samples | and filter for number of samples > 5.
### downloadSeriesMatrices will take the first two columns and dowload GSE-GPL.txt
### downloadSeriesAnnotations will take the first column and download GSE-annotation.txt
### packageData will take the first two columns to generate GSE-GPL.h5, then use the comma separated samples to identify the slices of the ARCHS4 matrix to put in.

#############################################
########## 1. Make Sample Table
#############################################

@follows(mkdir('s1-sample_table.dir'))

@merge(h5_files,
       's1-sample_table.dir/ARCHS-sample_table.txt')

def makeSampleTable(infiles, outfile):

	# Initialize list
	results = []

	# Loop through infiles
	for infile in infiles:

		# Read H5 file
		r = h5py.File(infile, 'r')

		# Get data
		gsm = [x.decode('utf-8') for x in r['meta']['Sample_geo_accession'].value]
		gse = [x.decode('utf-8').split('Xx-xX') for x in r['meta']['Sample_series_id'].value]
		gpl = [x.decode('utf-8') for x in r['meta']['Sample_platform_id'].value]

		# Add results
		for i, series_list in enumerate(gse):
			for series in series_list:
				results.append({'gse': series, 'gsm': gsm[i], 'gpl': gpl[i]})

	# Create dataframe
	results_dataframe = pd.DataFrame(results).groupby(['gpl', 'gse'])['gsm'].apply(lambda x: ', '.join(x)).rename('gsm').reset_index()

	# Filter samples
	results_dataframe['count'] = [len(x.split(', ')) for x in results_dataframe['gsm']]
	results_dataframe = results_dataframe[results_dataframe['count'] > 3]

	# Drop duplicate GSE
	results_dataframe.drop_duplicates('gse', inplace=True)
	
	# Save
	results_dataframe.to_csv(outfile, sep='\t', index=False)

#############################################
########## 2. Download Series Matrices
#############################################
##### Here we use the information regarding series contained in the ARCHS4 H5 files to download corresponding series matrices from GEO.
### Input: ARCHS4 H5 datasets for mouse and human.
### Output: Tab-separate table files containing series annotations downloaded from GEO.

@follows(mkdir('s2-series_matrices.dir'))

@subdivide(makeSampleTable,
		   formatter(),
		   's2-series_matrices.dir/*.txt',
		   's2-series_matrices.dir/')

def downloadSeriesMatrices(infile, outfiles, outfile_root):

	# Read dataframe
	series_dataframe = pd.read_table(infile)

	# Counter
	i = 0
	rows = len(series_dataframe.index)

	# Loop through series and platforms
	for gpl, gse in series_dataframe[['gpl', 'gse']].as_matrix():

		# Counter
		i += 1
		
		# Get outfile
		outfile = '{outfile_root}{gse}-{gpl}.txt'.format(**locals())

		# Only run if outfile doesn't exist
		if not os.path.exists(outfile):

			# Wait
			time.sleep(0.3)
			gsen = gse[:-3]+'nnn'

			# Get response
			try:
				url1 = 'ftp://ftp.ncbi.nlm.nih.gov/geo/series/{gsen}/{gse}/matrix/{gse}_series_matrix.txt.gz'.format(**locals())
				request = urllib.request.urlopen(urllib.request.Request(url1, headers={"Accept-Encoding": "gzip"})).read()
			except:
				try:
					url2 = 'ftp://ftp.ncbi.nlm.nih.gov/geo/series/{gsen}/{gse}/matrix/{gse}-{gpl}_series_matrix.txt.gz'.format(**locals())
					request = urllib.request.urlopen(urllib.request.Request(url2, headers={"Accept-Encoding": "gzip"})).read()
				except:
					print('Error downloading {url1} and {url2}'.format(**locals()))
					os.system('touch {}'.format(outfile))
					continue

			# Get Sample Metadata
			data = gzip.decompress(request).decode('utf-8', 'ignore')
			filtered_data = pd.DataFrame([x.replace('"', '').split('\t') for x in data.split('\n') if x.startswith('!Sample_characteristics_ch1') or x.startswith('!Sample_geo_accession')]).T
			filtered_data.columns = filtered_data.iloc[0]
			filtered_data = filtered_data.drop(0).set_index('!Sample_geo_accession')
			sample_metadata_dataframe = pd.DataFrame({index: {value.split(': ')[0]: value.split(': ')[1] for key, value in rowData.iteritems() if ': ' in value} for index, rowData in filtered_data.iterrows()}).T

			# Save
			print('Doing {gse}-{gpl} ({i}/{rows})...'.format(**locals()))
			sample_metadata_dataframe.to_csv(outfile, sep='\t', index=True)

#############################################
########## 3. Download Series Annotations
#############################################
##### Here we use the information regarding series contained in the ARCHS4 H5 files to download corresponding series metadata (title, summary, etc).
### Input: ARCHS4 H5 datasets for mouse and human.
### Output: JSON files containing series metadata downloaded from GEO.

@follows(mkdir('s3-series_metadata.dir'))

@subdivide(makeSampleTable,
		   formatter(),
		   's3-series_metadata.dir/*.txt',
		   's3-series_metadata.dir/')
		   
def getSeriesAnnotations(infile, outfiles, outfile_root):

	# Read dataframe
	series_dataframe = pd.read_table(infile)

	# Get GSEs
	gse_list = series_dataframe['gse'].unique()
	gses = len(gse_list)

	# Loop through GSE
	for i, gse in enumerate(gse_list):
		outfile = '{outfile_root}{gse}-annotation.txt'.format(**locals())
		if not os.path.exists(outfile):
			try:
				geoId = ET.fromstring(urllib.request.urlopen(
					'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term={}%5BAccession%20ID%5D'.format(gse)).read()).findall('IdList')[0][0].text
				root = ET.fromstring(urllib.request.urlopen(
					'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id={geoId}'.format(**locals())).read())
				annotated_dataset = {x.attrib['Name'].replace('PDAT', 'date'): x.text for x in root.find(
					'DocSum') if 'Name' in x.attrib.keys() and x.attrib['Name'] in ['title', 'summary', 'PDAT']}
				print('Downloaded {gse} ({i}/{gses})...'.format(**locals()))
			except:
				annotated_dataset = {x: '' for x in ['title', 'summary']}
				print('Error downloading {gse} ({i}/{gses})...'.format(**locals()))
			with open(outfile, 'w') as openfile:
				openfile.write(json.dumps(annotated_dataset))

#######################################################
#######################################################
########## S2. Prepare HDF5 Packages
#######################################################
#######################################################

#############################################
########## 1. Create HDF5 packages
#############################################
##### Here we use the information from the ARCHS4 H5 matrices and the downloaded metadata to generate packages for each series and platform.
### Input: ARCHS4 H5 datasets for mouse and human.
### Output: HDF5 data packages containing data and sample metadata for each series-platform.

# @follows(mkdir('s4-series_h5.dir'))

@subdivide(h5_files,
		   formatter(),
		   add_inputs(makeSampleTable),
		   's4-series_h5.dir/*.h5',
		   's4-series_h5.dir/')

def packageData(infiles, outfiles, outfile_root):

	# Split infiles
	h5_file, series_file = infiles

	# Read H5 data
	print('Reading {}...'.format(h5_file))
	r = h5py.File(h5_file, 'r')

	# Read series dataframe
	series_dataframe = pd.read_table(series_file)

	# Get matrix data
	expr = r['data']['expression'].value
	genes = r['meta']['genes'].value
	sample_accessions = r['meta']['Sample_geo_accession'].value
	sample_titles = r['meta']['Sample_title'].value

	# Get GSM index dictionary
	gsm_dict = {gsm.decode('utf-8'): i for i, gsm in enumerate(sample_accessions)}

	# Match indices
	series_dataframe['gsm_list'] = [x.split(', ') for x in series_dataframe['gsm']]
	series_dataframe['sample_index'] = [[gsm_dict.get(sample) for sample in samples] for samples in series_dataframe['gsm_list']]

	# Check if all samples are in series
	series_dataframe['all_samples'] = [all(x) for x in series_dataframe['sample_index']]

	# Drop series with at least one missing sample
	series_dataframe = series_dataframe.loc[series_dataframe['all_samples'], ['gpl', 'gse', 'sample_index']]

	# Counter
	i = 0
	rows = len(series_dataframe.index)

	# Get expression for each unique GSE-GPL pair
	for index, rowData in series_dataframe.iterrows():

		# Counter
		i += 1

		# Generate outfile
		outfile = '{outfile_root}{rowData[gse]}-{rowData[gpl]}.h5'.format(**locals())

		# Check if exists
		if not os.path.isfile(outfile):

			# Open h5
			# print('Writing {rowData[gse]}-{rowData[gpl]} ({i}/{rows})...'.format(**locals()))
			of = h5py.File(outfile, 'w')

			# Data
			data_grp = of.create_group('data')
			data_grp.create_dataset('expression', data=[expr[x] for x in rowData['sample_index']], chunks=True, dtype=int, compression="gzip")

			# Metadata
			gene_grp = of.create_group('meta/gene')
			gene_grp.create_dataset('symbol', data=genes, dtype=h5py.special_dtype(vlen=str))

			# Add sample title and accession
			sample_metadata_grp = of.create_group('meta/sample')
			sample_metadata_grp.create_dataset('Sample_title', data=[sample_titles[x] for x in rowData['sample_index']], dtype=h5py.special_dtype(vlen=str))
			sample_metadata_grp.create_dataset('Sample_geo_accession', data=[sample_accessions[x] for x in rowData['sample_index']], dtype=h5py.special_dtype(vlen=str))

			# Add sample metadata
			series_file = 's2-series_matrices.dir/{gse}-{gpl}.txt'.format(**rowData)
			if os.path.isfile(series_file):
				cols = []
				try:
					# Get data
					series_metadata_dataframe = pd.read_table(series_file).set_index('Unnamed: 0').rename(columns={'Sample_title': 'Sample_title_2'}).loc[[sample_accessions[x].decode('utf-8') for x in rowData['sample_index']]].T.dropna().T
					for column in series_metadata_dataframe.columns:
						try:
							sample_metadata_grp.create_dataset(column, data=series_metadata_dataframe[column], dtype=h5py.special_dtype(vlen=str))
							cols.append(column)
						except:
							pass

					# Print
					totcol = len(series_metadata_dataframe.columns)
					ncol = len(cols)
					message = 'Wrote {rowData[gse]}-{rowData[gpl]} ({i}/{rows}), with {ncol}/{totcol} metadata columns.'.format(**locals())
				except:
					message = 'Wrote {rowData[gse]}-{rowData[gpl]} ({i}/{rows}), without metadata.'

			# Close
			of.close()

			# Print
			print(message)

#######################################################
#######################################################
########## S3. Create JSON files
#######################################################
#######################################################

#############################################
########## 1. Build JSON
#############################################
##### Here we generate a JSON file containing information about each series, its platform and samples. These are used to build the database.
### Input: Series metadata and H5 files.
### Output: JSON files containing series and sample metadata.

@follows(mkdir('s5-series_json.dir'))

@transform(glob.glob('s4-series_h5.dir/*'),
		   regex(r'.*/(.*)-(.*).h5'),
		   add_inputs(r's3-series_metadata.dir/\1-annotation.txt'),
		   r's5-series_json.dir/\1-\2.json')

def buildSeriesJson(infiles, outfile):

	# Split infiles
	h5_file, annotation_file = infiles

	# Read H5 data
	print('Doing {}'.format(outfile))
	f = h5py.File(h5_file, 'r')

	# Try
	try:

		# Read series dataframe
		with open(annotation_file) as openfile:
			series_data = json.loads(openfile.read())

		# Skip if any field is missing
		if all([x for x in series_data.values()]):

			# Add sample metadata
			sample_metadata = pd.DataFrame({key: [x for x in value.value] if type(value) == h5py._hl.dataset.Dataset else [x for x in [y for y in value.items()][0][1].value] for key, value in f['meta']['sample'].items()}).set_index('Sample_geo_accession').rename(columns={'Sample_title': 'Sample Title'}).to_dict(orient='index')
			series_data.update({'samples': sample_metadata})

			# Add platform and series
			series_data.update({'platform_accession': h5_file.split('-')[-1].split('.')[0]})
			series_data.update({'dataset_accession': os.path.basename(h5_file).split('-')[0]})
			series_data.update({'type': 'rnaseq'})
			series_data.update({'dataset_title': series_data['title']})
			del series_data['title']

			# Write
			with open(outfile, 'w') as openfile:
				openfile.write(json.dumps(series_data, indent=4))

	# Exception
	except:
		print('Error doing {}'.format(outfile))

	# Close
	f.close()

#############################################
########## 2. Upload HDF5 packages
#############################################
##### Here we upload the HDF5 packages to Google Cloud.
### Input: ARCHS4 HDF5 packages.
### Output: Upload data to Google Cloud.

@follows(mkdir('s6-upload.dir'))
@transform(glob.glob('s5-series_json.dir/*'),
		   regex(r'.*/(.*).json'),
		   add_inputs(r's4-series_h5.dir/\1.h5'),
			r's6-upload.dir/\1-upload.txt')

def uploadData(infiles, outfile):

	# Split infiles
	json_file, h5_file = infiles

	# Get Bucket
	client = storage.Client()
	bucket = client.get_bucket('archs4-packages-v5')

	# Upload
	print('Doing {}'.format(h5_file))
	try:
		blob = bucket.blob(os.path.basename(h5_file))
		if not blob.exists():
			blob.upload_from_filename(h5_file)
			blob.make_public()
		os.system('touch {}'.format(outfile))
	except:
		print('There has been an error.')

##################################################
##################################################
########## Run pipeline
##################################################
##################################################
pipeline_run([sys.argv[-1]], multiprocess=5, verbose=1, forcedtorun_tasks=[])
print('Done!')
