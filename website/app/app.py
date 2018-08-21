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
from flask import Flask, request, render_template, Response, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy

##### 2. Python modules #####
import sys, os, json, requests, re, math, itertools, glob, urllib
import pandas as pd
import pymysql
from io import StringIO
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, or_, and_, func
pymysql.install_as_MySQLdb()

##### 3. Custom modules #####
sys.path.append('app/static/py')
import TableManager as TM
import ReadManager as RM

#############################################
########## 2. App Setup
#############################################
##### 1. Flask App #####
# General
with open('dev.txt') as openfile:
	dev = openfile.read() == 'True'
entry_point = '/biojupies-dev' if dev else '/biojupies'
app = Flask(__name__, static_url_path=os.path.join(entry_point, 'app/static'))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']#+'-dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
engine = db.engine
Session = sessionmaker(bind=engine)
metadata = MetaData()
metadata.reflect(bind=engine)
tables = metadata.tables

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
@app.route(entry_point+'/')
def index():

	# Get Carousel Images
	carousel_images = [os.path.basename(x).split('.')[0] for x in glob.glob('app/static/img/carousel/*.png')]#['notebook', 'pca', 'clustergrammer', 'volcano_plot', 'go_enrichment']
	carousel_images.sort()
	carousel_images.remove('template')

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
		{'link': 'published_data', 'icon': 'search', 'title': 'Published Data', 'description': 'Search thousands of published, publicly available datasets'},
		{'link': 'upload', 'icon': 'upload', 'title': 'Your Data', 'description': 'Upload your own gene expression data for analysis'},
		{'link': 'example', 'icon': 'question-circle', 'title': 'Example Data', 'description': 'Learn to generate notebooks with an example dataset'}
	]
	
	# Return result
	return render_template('analyze/analyze.html', options=options)

#############################################
########## 3. Search Data
#############################################
### Allows users to search indexed GEO datasets using text-based queries and other filtering parameters and to select them for notebook generation.
### Links to: search_data(), gtex().
### Accessible from: analyze(), navbar.


@app.route(entry_point+'/analyze/published_data')
def published_data():
	options = [
		{'link': 'search_data', 'image': 'geo', 'title': 'Gene Expression Omnibus', 'description': 'Search thousands of RNA-seq datasets published on <a href="https://www.ncbi.nlm.nih.gov/geo/" target="_blank">GEO</a>'},
		{'link': 'gtex', 'image': 'gtex', 'title': 'GTEx', 'description': 'Analyze RNA-seq samples from the publicly available <a href="https://www.gtexportal.org/home/" target="_blank">GTEx Portal</a>'}
	]
	return render_template('analyze/published_data.html', options=options)

#############################################
########## 3. Search Data
#############################################
### Allows users to search indexed GEO datasets using text-based queries and other filtering parameters and to select them for notebook generation.
### Links to: add_tools().
### Accessible from: published_data(), navbar.

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
	dataset_nr = pd.read_sql_query('SELECT COUNT(DISTINCT dataset_accession) FROM dataset_v5', engine).iloc[0,0]
	sample_nr = pd.read_sql_query('SELECT COUNT(DISTINCT sample_accession) FROM sample_v5', engine).iloc[0,0]

	###
	# Initialize database query
	session = Session()
	db_query = session.query(tables['dataset_v5'], tables['platform_v5'], func.count(tables['sample_v5'].columns['sample_accession']).label('nr_samples')) \
					.join(tables['sample_v5']) \
					.join(tables['platform_v5']) \
					.filter(or_( \
						tables['dataset_v5'].columns['dataset_title'].like('% '+q+' %'), \
						tables['dataset_v5'].columns['summary'].like('% '+q+' %'), \
						tables['dataset_v5'].columns['dataset_accession'].like(q)
					)) \
					.group_by(tables['dataset_v5'].columns['dataset_accession']) \
							.having(and_( \
								tables['platform_v5'].columns['organism'].in_(organisms), \
								func.count(tables['sample_v5'].columns['sample_accession']) >= min_samples,
								func.count(tables['sample_v5'].columns['sample_accession']) <= max_samples
							))

	# Sort query results
	if sortby == 'asc':
		db_query = db_query.order_by(func.count(tables['sample_v5'].columns['sample_accession']).asc())
	elif sortby == 'desc':
		db_query = db_query.order_by(func.count(tables['sample_v5'].columns['sample_accession']).desc())
	elif sortby == 'new':
		db_query = db_query.order_by(tables['dataset_v5'].columns['date'].desc())

	# Finish query
	query_dataframe = pd.DataFrame(db_query.all())
	session.close()

	# Filter dataset
	nr_results = len(query_dataframe.index)
	query_dataframe = query_dataframe.iloc[(page-1)*10:page*10]
	nr_results_displayed = max(len(query_dataframe.index), 10)

	# Get pages
	nr_pages = math.ceil(nr_results/10)
	if page == 1:
		pages = [x+1 for x in range(nr_pages)][:3]
	elif page == nr_pages:
		pages = [x+1 for x in range(nr_pages-3, nr_pages) if x>-1][-3:]
	else:
		pages = [page-1, page, page+1]

	# Add ...
	if nr_pages not in pages:
		if nr_pages-1 not in pages:
			pages.append('...')
		pages.append(nr_pages)

	# Highlight searched term
	if len(query_dataframe.index):
		h = lambda x: '<span class="highlight">{}</span>'.format(x)
		for col in ['dataset_title', 'summary']:
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

	# Check if dataset has been selected
	if request.args.get('uid') or request.form.get('gse-gpl') or request.form.get('gtex-samples-1'):

		# Get dataset information from request
		if request.args.get('uid'):
			selected_data = {'uid': request.args.get('uid'), 'source': 'upload'}
		elif request.form.get('gse-gpl'):
			selected_data = {'gse': request.form.get('gse-gpl').split('-')[0], 'gpl': request.form.get('gse-gpl').split('-')[1], 'source': 'archs4'}
		elif request.form.get('gtex-samples-1'):
			selected_data = {'source': 'gtex', 'gtex-samples-1': request.form.get('gtex-samples-1'), 'gtex-samples-2': request.form.get('gtex-samples-2')}

		# Perform tool and section query from database
		tools, sections = [pd.read_sql_table(x, engine) for x in ['tool', 'section']]
		tools = tools[tools['display'] == True]
		# tools = tools if dev else tools[tools['display'] == True]
		# if dev:
			# tools = tools[[x not in ['pathway_enrichment', 'tf_enrichment', 'kinase_enrichment', 'mirna_enrichment'] for x in tools['tool_string']]]
		tools, sections = [x.to_dict(orient='records') for x in [tools, sections]]

		# Combine tools and sections
		for section in sections:
			section.update({'tools': [x for x in tools if x['section_fk'] == section['id']]})

		# Number of tools
		nr_tools = len(tools)

		# Version
		dev_str = '-dev' if dev else ''
		req =  urllib.request.Request('http://amp.pharm.mssm.edu/notebook-generator-server{}/api/version'.format(dev_str)) # this will make the method "POST"
		version = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))['latest_library_version']
		
		# Return result
		return render_template('analyze/add_tools.html', selected_data=selected_data, sections=sections, nr_tools=nr_tools, version=version)

	# Redirect to analyze page
	else:
		return redirect(url_for('analyze'))

#############################################
########## 5. Configure Analysis
#############################################
### Responsible for handling the definition of the parameters for notebook configuration:
### - Defining groups, if tools require signature.
### - Defining optiona notebook and tool parameters.
### Links to: generate_notebook().
### Accessible from: add_tools().
##### CHECK QUERIES

@app.route(entry_point+'/analyze/configure', methods=['GET', 'POST'])
def configure_analysis():

	# Get form
	f=request.form

	# Check if form has been provided
	if f:

		# Check if requires signature
		signature_tools = pd.read_sql_query('SELECT tool_string FROM tool WHERE requires_signature = 1', engine)['tool_string'].values
		requires_signature = any([x in signature_tools for x in [x for x in f.lists()][0][-1]])
		print(f)

		# Signature generation
		if requires_signature and not f.get('source') == 'gtex':

			# Get metatada for processed datasets
			if 'gse' in request.form.keys():
				j = pd.read_sql_query('SELECT DISTINCT CONCAT(sample_accession, "---", sample_title) AS sample_info, variable, value FROM sample_v5 s LEFT JOIN dataset_v5 d ON d.id=s.dataset_fk LEFT JOIN sample_metadata_v5 sm ON s.id=sm.sample_fk WHERE dataset_accession = "{}"'.format(f.get('gse').replace('"', '')), engine)
				j = j.pivot(index='sample_info', columns='variable', values='value')
				j = pd.concat([pd.DataFrame({'accession': [x.split('---')[0] for x in j.index], 'sample': [x.split('---')[1] for x in j.index]}, index=j.index), j], axis=1).reset_index(drop=True).fillna('')
				j = j[[col for col, colData in j.iteritems() if len(colData.unique()) > 1]]

			# Get metadata for user-submitted dataset
			else:
				j = pd.read_sql_query('SELECT DISTINCT sample_name AS sample, variable, value FROM user_dataset ud LEFT JOIN user_sample us ON ud.id=us.user_dataset_fk LEFT JOIN user_sample_metadata usm ON us.id=usm.user_sample_fk WHERE ud.dataset_uid="{}"'.format(request.form.get('uid').replace('"', '')), engine)
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

			# Notebook title
			if f.get('group_a_label') and f.get('group_b_label'):
				notebook_title = ' vs '.join([f.get('group_a_label'), f.get('group_b_label')])
			elif f.get('gse'):
				notebook_title = f.get('gse')
			else:
				notebook_title = 'RNA-seq'
			notebook_title += ' Analysis Notebook | BioJupies'
		
			# Return result
			return render_template('analyze/review_analysis.html', t=t, f=f, notebook_title=notebook_title)

	# Redirect to analyze page
	else:
		# return render_template('analyze/review_analysis.html', t=[], f=f)
		return redirect(url_for('analyze'))

#############################################
########## 6. Generate Notebook
#############################################
### Displays the loading screen during notebook generation, and the link to the generated notebook once the process is complete.
### Links to: view_notebook().
### Accessible from: configure_analysis().
##### CHECK QUERIES

@app.route(entry_point+'/analyze/results', methods=['GET', 'POST'])
def generate_notebook():

	# Check if form has been provided
	if request.form:

		# Get form
		d = {key:value if len(value) > 1 else value[0] for key, value in request.form.lists()}

		# Get parameters and groups
		p = {x:{} for x in d['tool']} if isinstance(d['tool'], list) else {d['tool']: {}}
		g = {x:[] for x in ['a', 'b', 'none']}
		for key, value in d.items():
			if key not in ['sample-table_length', 'gtex-samples-1', 'gtex-samples-2', 'static_plots']:
				if '-' in key:
					if key.split('-')[0] in d['tool']:
						tool_string, parameter_string = key.split('-')
						p[tool_string][parameter_string] = value
					else:
						if value not in ['none', 'no', 'yes']:
							g[value[0]].append(key.rpartition('-')[0])

		### NEW
		# Plot type static
		if d.get('static-plots') == 'yes':
			static_tools = pd.read_sql_query('SELECT tool_string FROM tool t LEFT JOIN parameter p ON t.id=p.tool_fk WHERE parameter_string = "plot_type"', engine)['tool_string'].values
			for tool in static_tools:
				if tool in p.keys():
					p[tool]['plot_type'] = 'static'
		### NEW

		# Generate signature
		signature_tools = pd.read_sql_query('SELECT tool_string FROM tool WHERE requires_signature = 1', engine)['tool_string'].values
		requires_signature = any([x in signature_tools for x in p.keys()])
		if requires_signature:
			if d.get('source') == 'gtex':
				signature = {
					"method": "limma",
					"A": {"name": d.get('group_a_label', 'Group 1'), "samples": d['gtex-samples-1'].split(',')},
					"B": {"name": d.get('group_b_label', 'Group 2'), "samples": d['gtex-samples-2'].split(',')}
				}
			else:
				signature = {
					"method": "limma",
					"A": {"name": d.get('group_a_label', ''), "samples": g['a']},
					"B": {"name": d.get('group_b_label', ''), "samples": g['b']}
				}
		else:
			signature = {}

		# Get tags
		tags = d.get('tags', [])
		tags = tags if isinstance(tags, list) else [tags]

		# Version
		dev_str = '-dev' if dev else ''
		req =  urllib.request.Request('http://amp.pharm.mssm.edu/notebook-generator-server{}/api/version'.format(dev_str)) # this will make the method "POST"
		version = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))['latest_library_version']

		# Get source
		print(d)
		if 'gse' in d.keys() and 'gpl' in d.keys():
			data_parameters = {'gse': d['gse'], 'platform': d['gpl']}
		elif 'uid' in d.keys():
			data_parameters = {'uid': d['uid']}
		elif d['source'] == 'gtex':
			data_parameters = {'samples': d['gtex-samples-1'].split(',')+d['gtex-samples-2'].split(',')}


		# Generate notebook configuration
		c = {
			'notebook': {'title': d.get('notebook_title'), 'live': 'False', 'version': version},
			'tools': [{'tool_string': x, 'parameters': p.get(x, {})} for x in p.keys()],
			'data': {'source': d['source'], 'parameters': data_parameters},
			'signature': signature,
			'terms': tags
		}

		# Get tools
		tools = pd.read_sql_query('SELECT tool_string, tool_name FROM tool', engine).set_index('tool_string').to_dict()['tool_name']
		selected_tools = [tools[x['tool_string']] for x in c['tools']]
		
		# Return result
		return render_template('analyze/results.html', notebook_configuration=json.dumps(c), notebook_configuration_dict=c, selected_tools=selected_tools, dev=dev)
		# return json.dumps(c)

	# Redirect to analyze page
	else:
		return redirect(url_for('analyze'))

#############################################
########## 10. View Notebook
#############################################
### Displays the generated notebook to the user using nbviewer.
### Links to: none.
### Accessible from: generate_notebook().

@app.route(entry_point+'/notebook/<notebook_uid>')
def view_notebook(notebook_uid):

	# Get notebook data
	session = Session()
	db_query = session.query(tables['notebook'].columns['notebook_title'], tables['notebook'].columns['version']) \
						.filter(tables['notebook'].columns['notebook_uid'] == notebook_uid)
	query_results = [x._asdict() for x in db_query.all()]
	session.close()

	# Check if notebook has been found
	if len(query_results) == 1:

		# Get notebook data
		notebook_dict = query_results[0]

		# Whether to display HTTPS (Clustergrammer and L1000FWD only support HTTPS iframe in version >=v0.8)
		https = float('.'.join(notebook_dict['version'][1:].split('.')[:2])) > 0.7

		# Get Nbviewer URL and Title
		nbviewer_url = 'https://nbviewer.jupyter.org/urls/storage.googleapis.com/jupyter-notebook-generator/{notebook_uid}/{notebook_dict[notebook_title]}.ipynb'.format(**locals())

		# Replace HTTPS
		if not https:
			nbviewer_url = nbviewer_url.replace('https://', 'http://')

		# Return result
		return render_template('analyze/notebook.html', nbviewer_url=nbviewer_url, title=notebook_dict['notebook_title'], https=https)

	# Return 404
	else:
		abort(404)

#############################################
########## 11. GTEx Interface
#############################################
### Allows users to generate notebooks from GTEx data.
### Links to: .
### Accessible from: .

@app.route(entry_point+'/gtex')
def gtex():

	# Return
	return render_template('analyze/gtex.html')

##################################################
########## 2.2 APIs
##################################################

#############################################
########## 1. Ontology API
#############################################
### Returns a JSON of ontology terms.
### Input: a string specifying the ontology term category, specified by a GET parameter.
### Output: a JSON containing a list of elements with the following structure: [{"term_id": "", "term_name": "", "term_description": ""}, ...]
### Called by: review_notebook().

@app.route(entry_point+'/api/ontology')
def ontology_api():

	# Get category
	category = request.args.get('category')

	# Get ontologies
	if category in ['disease', 'drug']:
		ontologies = [category+'_ontology']
	elif category == 'sample_source':
		ontologies = ['cell_line_ontology', 'anatomy_ontology']
	else:
		ontologies = [category]

	# Initialize database query
	session = Session()
	db_query = session.query(tables['ontology_term']) \
					.join(tables['ontology']) \
					.filter(tables['ontology'].columns['ontology_string'].in_(ontologies))#.limit(5)
	# Finish query
	query_dataframe = pd.DataFrame(db_query.all()).drop(['ontology_fk'], axis=1).fillna('')
	session.close()

	# Return
	return json.dumps(query_dataframe.to_dict(orient='records'))

#############################################
########## 2. GTEx API
#############################################
### Returns a JSON containing GTEx sample metadata
### Links to: .
### Accessible from: .

@app.route(entry_point+'/api/gtex', methods=['POST'])
def gtex_api():

	# Read data
	gtex_data = pd.read_sql_query('SELECT "" AS checkbox, AGE AS Age, SMTS AS Tissue, SEX AS Gender, SAMPID AS id FROM gtex_metadata', engine).replace('1', 'Male').replace('2', 'Female').to_dict(orient='records')

	# Return
	return json.dumps(gtex_data)

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
########## 1. Upload Interface
#############################################
### Redirects users to the appropriate upload page, either for a gene expression table or for RNA-seq reads:
### Links to: upload_table(), upload_reads().
### Accessible from: analyze().

@app.route(entry_point+'/upload')
def upload():

	# Get options
	options = [
		{'link': 'upload_table', 'icon': 'table', 'title': 'Gene Expression Table', 'description': 'Table containing numeric gene counts, with samples on columns and gene symbols on rows'},
		{'link': 'upload_reads', 'icon': 'dna', 'title': 'Raw Sequencing Data', 'description': 'Raw FASTQ sample sequencing files generated from an RNA-seq profiling study'}
	]

	return render_template('upload/upload.html', options=options)

#############################################
########## 2. Upload Table Interface
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

#############################################
########## 3. Upload Reads
#############################################
### Allows users to upload FASTQ files for analysis.
### 1. upload_table.html, which contains a form to upload tabular gene expression data.
### 2. upload_metadata.html, which contains a form to upload metadata.
### 3. upload_table_loading.html, which contains a loader indicating that the data is being loaded.
### Accessible from: upload().
### APIs called: upload_dataframe_api(), upload_table_api().

@app.route(entry_point+'/upload/reads', methods=['GET', 'POST'])
def upload_reads():

	# Alignment settings
	if request.args.get('upload'):

		# Get upload UID
		upload_uid = request.args.get('upload')

		# Redirect if UID is short
		if len(upload_uid) < 11:
			return redirect(url_for('upload_reads'))
		
		# Else
		else:

			# Get samples
			req =  urllib.request.Request('https://amp.pharm.mssm.edu/charon/files?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}'.format(**os.environ))
			uploaded_files = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))['filenames']
			samples = [x for x in uploaded_files if x.startswith(upload_uid) and x.endswith('.fastq.gz')]

			### If UID doesn't exist in the database and files are matched, upload UID and files to database
			if len(samples):
				RM.uploadToDatabase(upload_uid, samples, session = Session(), tables=tables)
				return render_template('upload/align_reads.html', upload_uid=upload_uid, samples=samples)
			else:
				abort(404)

	# Alignment status
	elif request.args.get('alignment'):

		# Get form data
		alignment_uid = request.args.get('alignment')

		# Get jobs
		print('performing request...')
		req =  urllib.request.Request('https://amp.pharm.mssm.edu/cloudalignment/progress?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}'.format(**os.environ))
		job_dataframe = pd.DataFrame(json.loads(urllib.request.urlopen(req).read().decode('utf-8'))).T
		print('done!')
		jobs = job_dataframe.loc[[index for index, rowData in job_dataframe.iterrows() if rowData['outname'].startswith(alignment_uid)]].to_dict(orient='records')
		if len(jobs):

			### Add job to database, adding foreign key for upload
			RM.uploadJob(jobs, session=Session(), tables=tables)

			return render_template('upload/alignment_status.html', alignment_uid=alignment_uid, jobs=jobs, elysium_username=os.environ['ELYSIUM_USERNAME'], elysium_password=os.environ['ELYSIUM_PASSWORD'])

		else:
			abort(404)

	# Preview table
	elif request.args.get('table'):

		return render_template('upload/alignment_preview.html', alignment_uid=request.args.get('table'))

	# Annotate
	elif request.form.get('expression'):

		# Get form
		f = request.form

		# Get samples for group table
		samples = json.loads(f.to_dict()['expression'])['columns']
		samples.sort()

		# Get groups
		groups = [x for x in set([common_start(x, y) for x, y in itertools.combinations(samples, 2)]) if len(x)]
		groups.sort(key=len)

		# Assign groups
		matches = {sample: [group for group in groups if group in sample] for sample in samples}
		sample_groups = [{'sample': sample, 'group': matches[sample][-1] if len(matches[sample]) else ''} for sample in samples]
			
		# Return result
		return render_template('upload/upload_metadata.html', sample_groups=sample_groups, f=f, uploadtype='table')

	# Initial Upload
	else:

		# Get dataset UID
		upload_uid = TM.getUID(engine, idtype='upload')  # 'RTBO2Vk5xvV'  #

		# Render template
		return render_template('upload/upload_reads.html', upload_uid=upload_uid)

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
	dataframe.index = dataframe.index.astype(str)

	# Convert to JSON
	dataframe_json = json.dumps(dataframe.fillna('NA').to_dict(orient='split'))
	
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

	### Add table-alignment job FK, if provided

	# Get results
	dataset_uid_json = json.dumps({'dataset_uid': dataset_uid})
	
	# Return result
	return dataset_uid_json

#############################################
########## 3. Example Table API
#############################################
### Reads and example dataframe from the static source and returns it as a JSON
### Input: a JSON-formatted string containing one key: filename. It specifies the name of the file to return.
### Output: a JSON-formatted string generated using pd.to_dict(orient='split')
### Called by: upload_table().

@app.route(entry_point+'/api/upload/example', methods=['POST'])
def example_table_api():

	# Get file
	filename = request.json.get('filename')

	# Read file
	dataframe = pd.read_table('app/static/data/'+filename)

	# Set index
	dataframe.set_index(dataframe.columns[0], inplace=True)
	dataframe.index.name = ''

	# Convert to JSON
	dataframe_json = json.dumps(dataframe.to_dict(orient='split'))
	
	# Return result
	return dataframe_json

#############################################
########## 4. Launch Alignment API
#############################################
### Launches an alignment job given a set of FASTQ files, species, and settings regarding single-end or paired-end files. Returns a unique dataset ID.
### Input: a JSON-formatted string containing two keys: organism and sequencing-type. If sequencing-type is paired-end, additionally contains information about pairs.
### Output: a JSON-formatted string generated containing one key: dataset_UID.
### Called by: upload_reads().

@app.route(entry_point+'/api/upload/launch_alignment', methods=['GET', 'POST'])
def launch_alignment_api():

	# Get form
	alignment_settings = request.form.to_dict()
	# Get sample files
	if alignment_settings['sequencing-type'] == 'single-end':
		samples = [{'outname': value[:-len('.fastq.gz')], 'file1': value, 'file2': None} for key, value in alignment_settings.items() if key.startswith('file')]
	elif alignment_settings['sequencing-type'] == 'paired-end':
		sample_dataframe = pd.Series({key: value for key, value in alignment_settings.items() if key.startswith('sample')}).rename('values').to_frame()
		sample_dataframe['sample'] = [x.split('-')[0] for x in sample_dataframe.index]
		sample_dataframe['column'] = [x.split('-')[1] for x in sample_dataframe.index]
		samples = sample_dataframe.pivot(index='sample', columns='column', values='values').to_dict(orient='records')

	# Get alignment UID
	alignment_uid = TM.getUID(engine, 'alignment')

	# Loop through samples
	for sample in samples:

		# Add species
		sample['outname'] = alignment_uid+'-'+sample['outname']+'-'+alignment_settings['organism'].replace('human', 'hs').replace('mouse', 'mm')

		# Get jobs
		req =  urllib.request.Request('https://amp.pharm.mssm.edu/cloudalignment/progress?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}'.format(**os.environ))
		job_dataframe = pd.DataFrame(json.loads(urllib.request.urlopen(req).read().decode('utf-8'))).T[['outname', 'status']]

		# Check if alignment hasn't been submitted yet (fix to add support for different organisms)
		if sample['outname'] not in job_dataframe['outname'].tolist():

			# Get URL parameters
			params = '&'.join(['{key}={value}'.format(**locals()) for key, value in sample.items() if value])+'&organism='+alignment_settings['organism']
			url = "https://amp.pharm.mssm.edu/cloudalignment/createjob?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}&".format(**os.environ)+params

			# Launch alignment jobs
			req =  urllib.request.Request(url)
			resp = urllib.request.urlopen(req).read().decode('utf-8')
			print(resp)

	return json.dumps({'alignment_uid': alignment_uid})

#############################################
########## 5. Merge Counts API
#############################################
### Merges counts from Amazon S3 to a pandas dataframe based on a dataset UID.
### Input: a JSON-formatted string containing one key: alignment_uid. It specifies the UID of the count matrix to generate.
### Output: a JSON-formatted string generated using pd.to_dict(orient='split')
### Called by: upload_reads().

@app.route(entry_point+'/api/upload/merge_counts', methods=['GET', 'POST'])
def merge_counts_api():

	# Get dataset UID
	alignment_uid = request.args.get('alignment_uid')#'RTBO2Vk5xvV'

	# Get samples
	req =  urllib.request.Request('https://amp.pharm.mssm.edu/charon/files?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}'.format(**os.environ))
	uploaded_files = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))['filenames']
	samples = [x for x in uploaded_files if x.startswith(alignment_uid) and x.endswith('_gene.tsv')]

	# Initialize dict
	results = []

	# Read
	for sample in samples:

		# Get sample name
		sample_name = sample[(len(alignment_uid)+1)*2:-len('-hs_gene.tsv')]

		# Get counts from S3
		req =  urllib.request.Request('https://s3.amazonaws.com/biodos/c095573dc866f2db2cd39862ad89f074/'+sample)

		# Build dataframe
		counts = pd.read_table(StringIO(urllib.request.urlopen(req).read().decode('utf-8')), header=None, names=['gene_symbol', 'counts'])
		counts['counts'] = counts['counts'].astype(int)
		counts['sample'] = sample_name
		
		# Append
		results.append(counts)

	# Create dataframe
	count_dataframe = pd.concat(results).pivot_table(index='gene_symbol', columns='sample', values='counts')

	# Return
	return json.dumps(count_dataframe.to_dict(orient='split'))

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
### Accessible from: index().
### APIs called: contribute_api()

@app.route(entry_point+'/contribute', methods=['GET', 'POST'])
def contribute():
	return render_template('contribute.html')

#######################################################
#######################################################
########## 5. Docker
#######################################################
#######################################################
##### Handles information about Docker containers.

##################################################
########## 3.1 Webpages
##################################################

#############################################
########## 1. Docker Containers
#############################################
### Allows users to re-run notebooks using Docker containers.
### Accessible from: navbar.

@app.route(entry_point+'/docker')
def docker():
	return render_template('docker.html')

##################################################
########## 3.2 APIs
##################################################

#############################################
########## 1. Notebook API
#############################################
### Return a JSON file of notebook data based on a notebook UID.
### Input: A notebook UID.
### Output: A JSON containing notebook data.
### Called by: Docker container.

@app.route(entry_point+'/api/notebook/<notebook_uid>', methods=['GET'])
def notebook_api(notebook_uid):

	# Open session
	session = Session()
	
	# Initialize database query
	db_query_results = session.query(tables['notebooks']).filter(tables['notebooks'].columns['notebook_uid'] == notebook_uid).all()

	# Close session
	session.close()

	# If results
	if len(db_query_results):
		notebook_data = db_query_results[0]._asdict()
		notebook_data['date'] = notebook_data['date'].strftime('%b %d, %Y')
		del notebook_data['notebook_configuration']
		del notebook_data['id']
	else:
		notebook_data = {}

	# Return
	return json.dumps(notebook_data)

#######################################################
#######################################################
########## 6. Help
#######################################################
#######################################################
##### Help center.

##################################################
########## 3.1 Webpages
##################################################

#############################################
########## 1. Help Center
#############################################
### User manual.
### Accessible from: navbar.

@app.route(entry_point+'/help')
def help():
	with open('app/static/help/sections.json') as openfile:
		categories = json.load(openfile)
	return render_template('help.html', categories=categories, entry_point=entry_point)

#############################################
########## 2. Example Dataset
#############################################
### Example dataset.
### Accessible from: analyze().

@app.route(entry_point+'/analyze/example')
def example():

	# Select dataset
	dataset_accession = 'GSE88741'
	dataset = pd.read_sql_query('SELECT platform_accession, dataset_accession, dataset_title, summary, date, count(*) AS nr_samples, organism FROM dataset_v5 d LEFT JOIN sample_v5 s ON d.id=s.dataset_fk LEFT JOIN platform_v5 p ON p.id=s.platform_fk WHERE dataset_accession = "{}"'.format(dataset_accession), engine).drop_duplicates().T.to_dict()[0]
	# dataset['date'] = dataset['date'].strftime('%b %d, %Y')
	return render_template('analyze/example.html', dataset=dataset)

##################################################
########## 3.2 APIs
##################################################

#############################################
########## 1. Statistics
#############################################

@app.route(entry_point+'/api/stats')
def stats_api():
	
	# Get object
	obj = request.args.get('obj')

	# Check object
	if obj in ['notebook', 'tool', 'dataset_v5', 'user_dataset', 'fastq_file', 'sample_v5']:

		# Get notebook data
		session = Session()
		query = session.query(func.count(tables[obj].columns['id']))
		if obj == 'tool':
			query = query.filter(tables[obj].columns['display'] == 1)
		n = query.all()[0][0]
		session.close()

		# Return
		return json.dumps({'n': n})
	else:
		abort(404)


#######################################################
#######################################################
########## 6. Handlers
#######################################################
#######################################################
##### 404 and error handlers.

##################################################
########## 3.1 Error Handlers
##################################################

#############################################
########## 1. 404
#############################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

#############################################
########## 2. 500
#############################################
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

#######################################################
#######################################################
########## 7. Run App
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################
