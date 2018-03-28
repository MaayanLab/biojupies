#################################################################
#################################################################
############### Notebook Generator Website ######################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#######################################################
#######################################################
########## 1. App Configuration
#######################################################
#######################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. Flask modules #####
from flask import Flask, request, render_template, Response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

##### 2. Python modules #####
import sys, os, json, requests, re, math, itertools, glob
import pandas as pd
import pymysql
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, or_, and_, func
pymysql.install_as_MySQLdb()

##### 3. Custom modules #####
sys.path.append('static/py')
import TableManager as TM

#############################################
########## 2. App Setup
#############################################
##### 1. Flask App #####
# General
entry_point = '/notebook-generator-website'
app = Flask(__name__, static_url_path=os.path.join(entry_point, 'static'))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']#+'-dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
engine = db.engine
Session = sessionmaker(bind=engine)
metadata = MetaData()
metadata.reflect(bind=engine)
tables = metadata.tables

# Notebook Generation
version = 'v0.5'

##### 2. Functions #####
# Longest common substring
def common_start(sa, sb):
	def _iter():
		for a, b in zip(sa, sb):
			if a == b:
				yield a
			else:
				return
	return ''.join(_iter()).rstrip('-').rstrip('.').rstrip('_')

#######################################################
#######################################################
########## 2. Notebook Generation
#######################################################
#######################################################
##### Handles routes used to generate notebooks.

##################################################
########## 2.1 Webpages
##################################################

#############################################
########## 1. Home
#############################################
### Landing page for the website. Links to analyze() endpoint.
### Links to: analyze().

@app.route(entry_point)
def index():

	# Get Carousel Images
	carousel_images = [os.path.basename(x).split('.')[0] for x in glob.glob('static/img/carousel/*.png')]#['notebook', 'pca', 'clustergrammer', 'volcano_plot', 'go_enrichment']
	carousel_images.sort()
	print(carousel_images)

	return render_template('index.html', carousel_images=carousel_images)

#############################################
########## 2. Analyze
#############################################
### Provides users with three different options to use the resource.
### Links to: search_data(), upload_table(), and tutorial().
### Accessible from: index().

@app.route(entry_point+'/analyze')
def analyze():

	# Get options
	options = [
		{'link': 'search_data', 'icon': 'search', 'title': 'Search', 'description': 'Search thousands of ready-to-analyze datasets'},
		{'link': 'upload_table', 'icon': 'upload', 'title': 'Upload', 'description': 'Upload your own<br>gene expression data<br>for analysis'},
		{'link': 'index', 'icon': 'question-circle', 'title': 'Tutorial', 'description': 'Learn to generate notebooks with a<br>sample dataset'}
	]
	
	# Return result
	return render_template('analyze/analyze.html', options=options)

#############################################
########## 3. Search Data
#############################################
### Allows users to search indexed GEO datasets using text-based queries and other filtering parameters and to select them for notebook generation.
### Links to: add_tools().
### Accessible from: analyze(), navbar.

@app.route(entry_point+'/analyze/search')
def search_data():

	# Get Search Parameters
	q = request.args.get('q', 'cancer')
	min_samples = request.args.get('min_samples', 6)
	max_samples = request.args.get('max_samples', 30)
	max_samples = 500 if max_samples == '70' else max_samples
	sortby = request.args.get('sortby', 'new')
	organism = request.args.get('organism', 'all')
	organisms = [x for x in ['Human', 'Mouse'] if organism == 'all' or x == organism.title()]
	page = int(request.args.get('page', '1'))

	# Get counts
	dataset_nr = pd.read_sql_query('SELECT COUNT(DISTINCT gse) FROM series', engine).iloc[0,0]
	sample_nr = pd.read_sql_query('SELECT COUNT(DISTINCT gsm) FROM sample', engine).iloc[0,0]

	###
	# Initialize database query
	session = Session()
	db_query = session.query(tables['series'], tables['platform'], func.count(tables['sample'].columns['gsm']).label('nr_samples')) \
					.join(tables['sample']) \
					.join(tables['platform']) \
					.filter(or_( \
						tables['series'].columns['title'].like('% '+q+' %'), \
						tables['series'].columns['summary'].like('% '+q+' %'), \
						tables['series'].columns['gse'].like(q) \
					)) \
					.group_by(tables['series'].columns['gse']) \
					.having(and_( \
						tables['platform'].columns['organism'].in_(organisms), \
						func.count(tables['sample'].columns['gsm']) >= min_samples, \
						func.count(tables['sample'].columns['gsm']) <= max_samples \
					))

	# Sort query results
	if sortby == 'asc':
		db_query = db_query.order_by(func.count(tables['sample'].columns['gsm']).asc())
	elif sortby == 'desc':
		db_query = db_query.order_by(func.count(tables['sample'].columns['gsm']).desc())
	elif sortby == 'new':
		db_query = db_query.order_by(tables['series'].columns['date'].desc())

	# Finish query
	query_dataframe = pd.DataFrame(db_query.all())
	session.close()

	# Filter dataset
	nr_results = len(query_dataframe.index)
	query_dataframe = query_dataframe.iloc[(page-1)*10:page*10]
	nr_results_displayed = len(query_dataframe.index)

	# Get pages
	nr_pages = math.ceil(nr_results/10)
	if page == 1:
		pages = [x+1 for x in range(nr_pages)][:3]
	elif page == nr_pages:
		pages = [x+1 for x in range(nr_pages-3, nr_pages) if x>-1][-3:]
	else:
		pages = [page-1, page, page+1]

	# Highlight searched term
	if len(query_dataframe.index):
		h = lambda x: '<span class="highlight">{}</span>'.format(x)
		for col in ['title', 'summary']:
			query_dataframe[col] = [x.replace(q, h(q)).replace(q.title(), h(q.title())).replace(q.lower(), h(q.lower())).replace(q.upper(), h(q.upper())) for x in query_dataframe[col]]

	# Convert to dictionary
	datasets = query_dataframe.to_dict(orient='records')
	
	# Return result
	return render_template('analyze/search_data.html', datasets=datasets, min_samples=min_samples, max_samples=max_samples, q=q, nr_results=nr_results, nr_results_displayed=nr_results_displayed, pages=pages, page=page, organism=organism, sortby=sortby, nr_pages=nr_pages, dataset_nr=dataset_nr, sample_nr=sample_nr)

#############################################
########## 4. Add Tools
#############################################
### Allows users to select one or more tools to add to the notebook.
### Links to: configure_analysis().
### Accessible from: search_data(), .

@app.route(entry_point+'/analyze/tools', methods=['GET', 'POST'])
def add_tools():

	# Get dataset information from request
	selected_data = {'uid': request.args.get('uid'), 'source': 'upload'} if 'uid' in request.args.keys() else {'gse': request.form.get('gse-gpl').split('-')[0], 'gpl': request.form.get('gse-gpl').split('-')[1], 'source': 'archs4'}

	# Perform tool and section query from database
	tools, sections = [pd.read_sql_table(x, engine).to_dict(orient='records') for x in ['tool', 'section']]

	# Combine tools and sections
	for section in sections:
		section.update({'tools': [x for x in tools if x['section_fk'] == section['id']]})

	# Number of tools
	nr_tools = len(tools)
	
	# Return result
	return render_template('analyze/add_tools.html', selected_data=selected_data, sections=sections, nr_tools=nr_tools)

#############################################
########## 5. Configure Analysis
#############################################
### Responsible for handling the definition of the parameters for notebook configuration:
### - Defining groups, if tools require signature.
### - Defining optiona notebook and tool parameters.
### Links to: generate_notebook().
### Accessible from: add_tools().

@app.route(entry_point+'/analyze/configure', methods=['GET', 'POST'])
def configure_analysis():

	# Get form
	f=request.form

	# Check if requires signature
	signature_tools = pd.read_sql_query('SELECT tool_string FROM tool WHERE requires_signature = 1', engine)['tool_string'].values
	requires_signature = any([x in signature_tools for x in [x for x in f.lists()][0][-1]])

	# Signature generation
	if requires_signature:

		# Get metatada for processed datasets
		if 'gse' in request.form.keys():
			j = pd.read_sql_query('SELECT DISTINCT CONCAT(gsm, "---", sample_title) AS sample_info, variable, value FROM sample s LEFT JOIN series g ON g.id=s.series_fk LEFT JOIN sample_metadata sm ON s.id=sm.sample_fk WHERE gse = "{}"'.format(f.get('gse')), engine).pivot(index='sample_info', columns='variable', values='value')
			j = pd.concat([pd.DataFrame({'accession': [x.split('---')[0] for x in j.index], 'sample': [x.split('---')[1] for x in j.index]}, index=j.index), j], axis=1).reset_index(drop=True).fillna('')
			j = j[[col for col, colData in j.iteritems() if len(colData.unique()) > 1]]

		# Get metadata for user-submitted dataset
		else:
			j = pd.read_sql_query('SELECT DISTINCT sample_name AS sample, variable, value FROM user_dataset ud LEFT JOIN user_sample us ON ud.id=us.user_dataset_fk LEFT JOIN user_sample_metadata usm ON us.id=usm.user_sample_fk WHERE ud.dataset_uid="{}"'.format(request.form.get('uid')), engine)
			j = j.pivot(index='sample', columns='variable', values='value').reset_index()
	
		# Return result
		return render_template('analyze/configure_signature.html', f=f, j=j)

	else:

		# Get tool query
		tools = [value for value, key in zip(f.listvalues(), f.keys()) if key == 'tool'][0]
		tool_query_string = '("'+'","'.join([value for value, key in zip(f.listvalues(), f.keys()) if key == 'tool'][0])+'")'
		p = pd.read_sql_query('SELECT tool_name, tool_string, tool_description, parameter_name, parameter_description, parameter_string, value, `default` FROM tool t LEFT JOIN parameter p ON t.id=p.tool_fk LEFT JOIN parameter_value pv ON p.id=pv.parameter_fk WHERE t.tool_string IN {}'.format(tool_query_string), engine).set_index(['tool_string'])#.set_index(['tool_name', 'parameter_name', 'parameter_description', 'parameter_string'])

		# Fix tool parameter data structure
		t = p[['tool_name', 'tool_description']].drop_duplicates().reset_index().set_index('tool_string', drop=False).to_dict(orient='index')#.groupby('tool_string')[['tool_name', 'tool_description']]#.apply(tuple).to_frame()#drop_duplicates().to_dict(orient='index')
		p_dict = {tool_string: p.drop(['tool_description', 'tool_name', 'value', 'default'], axis=1).loc[tool_string].drop_duplicates().to_dict(orient='records') if not isinstance(p.loc[tool_string], pd.Series) else [] for tool_string in tools}
		for tool_string, parameters in p_dict.items():
			for parameter in parameters:
				parameter['values'] = p.reset_index().set_index(['tool_string', 'parameter_string'])[['value', 'default']].dropna().loc[(tool_string, parameter['parameter_string'])].to_dict(orient='records')
		for tool_string in t.keys():
			t[tool_string]['parameters'] = p_dict[tool_string]
		t = [t[x] for x in tools]
	
		# Return result
		return render_template('analyze/review_analysis.html', t=t, f=f)

#############################################
########## 6. Generate Notebook
#############################################
### Displays the loading screen during notebook generation, and the link to the generated notebook once the process is complete.
### Links to: view_notebook().
### Accessible from: configure_analysis().

@app.route(entry_point+'/analyze/results', methods=['GET', 'POST'])
def generate_notebook():

	# Get form
	d = {key:value if len(value) > 1 else value[0] for key, value in request.form.lists()}

	# Get parameters and groups
	p = {x:{} for x in d['tool']}
	g = {x:[] for x in ['a', 'b', 'none']}
	for key, value in d.items():
		if key not in ['sample-table_length']:
			if '-' in key:
				if key.split('-')[0] in d['tool']:
					tool_string, parameter_string = key.split('-')
					p[tool_string][parameter_string] = value
				else:
					if value != 'none':
						g[value[0]].append(key.rpartition('-')[0])

	# Generate notebook configuration
	c = {
		'notebook': {'title': d.get('notebook_title'), 'live': 'False', 'version': version},
		'tools': [{'tool_string': x, 'parameters': p.get(x, {})} for x in d['tool']],
		'data': {'source': d['source'], 'parameters': {'gse': d['gse'], 'platform': d['gpl']} if 'gse' in d.keys() and 'gpl' in d.keys() else {'uid': d['uid']}},
		'signature': {"method": "limma",
			"A": {"name": d.get('group_a_label'), "samples": g['a']},
			"B": {"name": d.get('group_b_label'), "samples": g['b']}}
	}

	# Get tools
	tools = pd.read_sql_query('SELECT tool_string, tool_name FROM tool', engine).set_index('tool_string').to_dict()['tool_name']
	tool_string = ', '.join([tools[x['tool_string']] for x in c['tools']])
	
	# Return result
	return render_template('analyze/results.html', notebook_configuration=json.dumps(c), notebook_configuration_dict=c, tool_string=tool_string)

#############################################
########## 10. View Notebook
#############################################
### Displays the generated notebook to the user using nbviewer.
### Links to: none.
### Accessible from: generate_notebook().

@app.route(entry_point+'/notebooks/<notebook_uid>')
def view_notebook(notebook_uid):

	# Get notebook data
	notebook_data = pd.read_sql_query('SELECT notebook_url, notebook_configuration FROM notebooks WHERE notebook_uid="{notebook_uid}"'.format(**locals()), engine).to_dict(orient='index')[0]

	# Get Nbviewer URL and Title
	nbviewer_url = 'http://nbviewer.jupyter.org/urls/'+notebook_data['notebook_url'].replace('https://', '')
	title = json.loads(notebook_data['notebook_configuration'])['notebook']['title']
	
	# Return result
	return render_template('analyze/notebook.html', nbviewer_url=nbviewer_url, title=title)

#######################################################
#######################################################
########## 3. Data Upload
#######################################################
#######################################################
##### Handles routes used to handle expression tables uploaded by users.

##################################################
########## 3.1 Webpages
##################################################

#############################################
########## 1. Upload Table Interface
#############################################
### Allows users to upload a gene expression table. Renders three templates:
### 1. upload_table.html, which contains a form to upload tabular gene expression data.
### 2. upload_metadata.html, which contains a form to upload metadata.
### 3. upload_table_loading.html, which contains a loader indicating that the data is being loaded.
### Links to: add_tools().
### Accessible from: analyze(), navbar.
### APIs called: upload_dataframe_api(), upload_table_api().

@app.route(entry_point+'/upload/table', methods=['GET', 'POST'])
def upload_table():

	# Get form
	f = request.form
	
	# Return upload expression table form
	if not len(f):
		return render_template('upload/upload_table.html')
	
	# Return upload dataset metadata form
	elif 'metadata' not in f.to_dict().keys():

		# Get samples for group table
		samples = json.loads(f.to_dict()['expression'])['columns']
		samples.sort()

		# Get groups
		groups = [x for x in set([common_start(x, y) for x, y in itertools.combinations(samples, 2)]) if len(x)]
		groups.sort(key=len)

		# Assign groups
		matches = {sample: [group for group in groups if group in sample] for sample in samples}
		print(matches)
		sample_groups = [{'sample': sample, 'group': matches[sample][-1] if len(matches[sample]) else ''} for sample in samples]
			
		# Return result
		return render_template('upload/upload_metadata.html', sample_groups=sample_groups, f=f, uploadtype='table')

	# Process metadata dataframe
	else:

		# Get metadata dataframe
		metadata_dataframe = pd.DataFrame(json.loads(f['metadata'])).set_index(0)
		metadata_dataframe.columns = metadata_dataframe.iloc[0]
		metadata_dataframe = metadata_dataframe[1:]
		metadata_dataframe.index.name = 'Sample'
		metadata_dataframe.columns.name = ''
		metadata_dataframe = metadata_dataframe.loc[json.loads(f['expression'])['columns']]

		# Add to form
		f = f.to_dict()
		f['metadata'] = metadata_dataframe.to_dict(orient='split')
		f = json.dumps(f)
	
		# Return result
		return render_template('upload/upload_table_loading.html', f=f)

##################################################
########## 3.2 APIs
##################################################

#############################################
########## 1. Upload Dataframe API
#############################################
### Handles the uploading of any dataframe to the server backend.
### Input: a table-formatted file uploaded by the user.  Supports txt, tsv, csv, xls, xlsx
### Output: the data contained in the uploaded table, provided as a JSON-formatted string generated using pd.to_dict(orient='split')
### Called by: upload_table().

@app.route(entry_point+'/api/upload/dataframe', methods=['POST'])
def upload_dataframe_api():

	# Get file
	f = request.files.get('file')

	# Read file
	f_format = f.filename.split('.')[-1]
	if f_format in ['txt', 'tsv']:
		dataframe = pd.read_table(f)
	elif f_format == 'csv':
		dataframe = pd.read_csv(f)
	elif f_format in ['xls', 'xlsx']:
		dataframe = pd.read_excel(f)

	# Set index
	dataframe.set_index(dataframe.columns[0], inplace=True)
	dataframe.index.name = ''

	# Convert to JSON
	dataframe_json = json.dumps(dataframe.to_dict(orient='split'))
	
	# Return result
	return dataframe_json

#############################################
########## 2. Upload Table API
#############################################
### Packages the uploaded gene expression data/metadata and uploads it to the cloud.
### Input: a JSON-formatted string containing two keys: 'expression' and 'metadata'. These contain respectively user-submitted expression and metadata, processed using upload_dataframe_api().
### Output: the data contained in the uploaded table, provided as a JSON-formatted string generated using pd.to_dict(orient='split')
### Called by: upload_table().

@app.route(entry_point+'/api/upload/table', methods=['POST'])
def upload_table_api():

	# Read data
	data = request.json
	data['expression'] = json.loads(data['expression'])

	# Get UID
	dataset_uid = TM.getUID(engine)

	# Build H5
	h5_file = TM.buildH5(data, dataset_uid)

	# Upload to Bucket
	TM.uploadH5(h5_file, dataset_uid)

	# Upload to database
	TM.uploadToDatabase(data, dataset_uid, engine)

	# Get results
	dataset_uid_json = json.dumps({'dataset_uid': dataset_uid})
	
	# Return result
	return dataset_uid_json

#######################################################
#######################################################
########## 4. Contribution
#######################################################
#######################################################
##### Handles plugins uploaded by users.

##################################################
########## 3.1 Webpages
##################################################

#############################################
########## 1. Contribute Plugin Interface
#############################################
### Allows users to upload a plugin for evaluation.
### Accessible from: navbar.
### APIs called: upload_dataframe_api(), upload_table_api().

@app.route(entry_point+'/contribute')
def contribute():
	return ''

#######################################################
#######################################################
########## 5. About
#######################################################
#######################################################
##### Help center.

##################################################
########## 3.1 Webpages
##################################################

#############################################
########## 1. Contribute Plugin Interface
#############################################
### User manual.
### Accessible from: navbar.

@app.route(entry_point+'/about')
def about():
	return ''

#######################################################
#######################################################
########## 6. Run App
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')