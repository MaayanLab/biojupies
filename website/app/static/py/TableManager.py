#################################################################
#################################################################
############### Table Manager API ###############################
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
import random
import string
import json
import h5py
import os
import datetime
import urllib.parse
import pandas as pd
from google.cloud import storage

#############################################
########## 2. Variables
#############################################

#################################################################
#################################################################
############### 1. Expression Table #############################
#################################################################
#################################################################

#############################################
########## 1. Get UID
#############################################

def getUID(engine, idtype='table'):

	# Set duplicate
	duplicate = True

	# Get UID
	while duplicate:

		# Random UID
		uid = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))
		if idtype == 'table':
			uid = 'ET'+uid
		elif idtype == 'upload':
			uid = 'RU'+uid
		elif idtype == 'alignment':
			uid = 'AJ'+uid

		# Check if exists
		duplicate = len(pd.read_sql_query('SELECT * FROM user_dataset WHERE dataset_uid = "{}"'.format(uid), engine).index)

	# Return
	return uid

#############################################
########## 2. Build H5
#############################################

def buildH5(data, dataset_uid):

	# Get outfile
	outfile = os.path.join('app/static/uploads/h5', dataset_uid+'.h5')
	os.makedirs(os.path.dirname(outfile), exist_ok=True)

	# Try
	try:

		# Get outfile
		f = h5py.File(outfile, 'w')

		# Add data
		data_grp = f.create_group('data')
		data_grp.create_dataset('expression', data=data['expression']['data'])

		# Add gene metadata
		gene_grp = f.create_group('meta/gene')
		gene_grp.create_dataset('symbol', data=[x.encode('utf-8') for x in data['expression']['index']], dtype=h5py.special_dtype(vlen=str))

		# Add sample metadata
		samples = data['expression']['columns']
		metadata_dataframe = pd.DataFrame(index=data['metadata']['index'], columns=data['metadata']['columns'], data=data['metadata']['data']).loc[samples].reset_index().rename(columns={'index': 'Sample'}) #####
		sample_metadata_grp = f.create_group('meta/sample')
		for col in metadata_dataframe.columns:
			sample_metadata_grp.create_dataset(col, data=[x.encode('utf-8') for x in metadata_dataframe[col]], dtype=h5py.special_dtype(vlen=str))

		# Add QC
		if data.get('qc'):
			sequencing_grp = f.create_group('meta/sequencing')
			sequencing_grp.create_dataset('qc', data=data['qc'], dtype=h5py.special_dtype(vlen=str))
			sequencing_grp.create_dataset('reference_genome', data=data.get('reference_genome'), dtype=h5py.special_dtype(vlen=str))


		# Close file
		f.close()

	# Except
	except:

		# Remove outfile
		os.unlink(outfile)
		outfile = None

	# Return
	return outfile

#############################################
########## 3. Upload to Cloud
#############################################

def uploadH5(h5_file, dataset_uid):
	
	# Upload to Bucket
	client = storage.Client()
	bucket = client.get_bucket('jupyter-notebook-generator-user-data')
	blob = bucket.blob('{dataset_uid}/{dataset_uid}.h5'.format(**locals()))
	blob.upload_from_filename(h5_file, content_type='text/html')
	blob.make_public()

	# Remove file
	os.unlink(h5_file)

#############################################
########## 4. Upload to Database
#############################################
### ToDo
def uploadToDatabase(data, dataset_uid, engine, user_id, dataset_title, alignment_uid, session, tables):

	# Get alignment FK
	alignment = session.query(tables['fastq_alignment']).filter(tables['fastq_alignment'].columns['alignment_uid'] == alignment_uid).first()
	fastq_alignment_fk = None if not alignment else alignment.id

	# Upload dataset and get FK
	print(True if user_id else False)
	dataset_id = session.execute(tables['user_dataset'].insert({'dataset_uid': dataset_uid, 'dataset_title': dataset_title, 'user_fk': user_id, 'fastq_alignment_fk': fastq_alignment_fk, 'private': True if user_id else False})).lastrowid
	session.commit()
	session.close()

	# Get metadata
	metadata_dataframe = pd.DataFrame(index=data['metadata']['index'], columns=data['metadata']['columns'], data=data['metadata']['data']).rename(columns={'index': 'Sample'})
	metadata_dataframe.index.name = 'sample_name'

	# Upload samples
	sample_dataframe = metadata_dataframe.index.to_frame().reset_index(drop=True)
	sample_dataframe['user_dataset_fk'] = dataset_id
	sample_dataframe.to_sql('user_sample', engine, if_exists='append', index=False)

	# Get sample FK
	sample_names = '", "'.join(sample_dataframe['sample_name'])
	sample_fk_dataframe = pd.read_sql_query('SELECT sample_name, id AS user_sample_fk FROM user_sample WHERE user_dataset_fk = {dataset_id} AND sample_name IN ("{sample_names}")'.format(**locals()), engine)

	# Upload sample metadata
	sample_metadata_dataframe = pd.melt(metadata_dataframe.reset_index(), id_vars='sample_name').merge(sample_fk_dataframe, on='sample_name').drop('sample_name', axis=1)
	sample_metadata_dataframe.to_sql('user_sample_metadata', engine, if_exists='append', index=False)

#############################################
########## 5. Upload Table
#############################################
### UNUSED?

def uploadTable(data, engine):

	# Get UID
	dataset_uid = getUID(engine)

	# Read data
	data = json.loads(data)
	data['expression'] = json.loads(data['expression'])

	# Build H5
	h5_file = buildH5(data, dataset_uid)

	# Upload to Bucket
	uploadH5(h5_file, dataset_uid)

	# Upload to database
	uploadToDatabase(data, dataset_uid, engine)

	# Get results
	results = json.dumps({'dataset_uid': dataset_uid})

	return results

