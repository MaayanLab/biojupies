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
from flask import Flask, request, render_template, Response, redirect, url_for, abort, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
# from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import (
	LoginManager, UserMixin, current_user,
	login_required, login_user, logout_user
)
from werkzeug.contrib.fixers import ProxyFix

##### 2. Python modules #####
# General
import sys, os, json, requests, re, math, itertools, glob, urllib
import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime

# Database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData, or_, and_, func
import pymysql
pymysql.install_as_MySQLdb()

# Sentry
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

##### 3. Custom modules #####
sys.path.append('app/static/py')
import TableManager as TM
import ReadManager as RM
import Query as Q

#############################################
########## 2. General App Setup
#############################################
##### 1. Flask App #####
# Sentry
if os.getenv('SENTRY_DSN'):
	sentry_sdk.init(dsn=os.environ['SENTRY_DSN'], integrations=[FlaskIntegration()])

# General
with open('dev.txt') as openfile:
	dev = openfile.read() == 'True'
entry_point = '/biojupies-dev' if dev else '/biojupies'
app = Flask(__name__, static_url_path='/app/static')

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
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

#############################################
########## 3. Middleware
#############################################
# Prefix middleware
class PrefixMiddleware(object):

	def __init__(self, app, prefix=''):
		self.app = app
		self.prefix = prefix

	def __call__(self, environ, start_response):
		if environ['PATH_INFO'].startswith(self.prefix):
			environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
			environ['SCRIPT_NAME'] = self.prefix
			return self.app(environ, start_response)
		else:
			start_response('404', [('Content-Type', 'text/plain')])
			return ["This url does not belong to the app.".encode()]
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=entry_point)

# HTTPS fix
if not os.environ.get('OAUTHLIB_INSECURE_TRANSPORT'):
	def _force_https(wsgi_app):
		def wrapper(environ, start_response):
			environ['wsgi.url_scheme'] = 'https'
			return wsgi_app(environ, start_response)
		return wrapper
	app.wsgi_app = _force_https(app.wsgi_app)

#############################################
########## 4. OAuth
#############################################
# Google Login
if os.environ.get('OAUTHLIB_INSECURE_TRANSPORT'):
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
app.secret_key = os.environ['SECRET_KEY']
# blueprint = make_github_blueprint(
# 	client_id=os.environ['GITHUB_CLIENT_ID'],
# 	client_secret=os.environ['GITHUB_CLIENT_SECRET'],
# 	redirect_to='dashboard'
# )
blueprint = make_google_blueprint(
	client_id=os.environ['GOOGLE_OAUTH_CLIENT_ID'],
	client_secret=os.environ['GOOGLE_OAUTH_CLIENT_SECRET'],
	redirect_to='dashboard',
	scope=[
		"https://www.googleapis.com/auth/plus.me",
		"https://www.googleapis.com/auth/userinfo.email",
	]
)
app.register_blueprint(blueprint, url_prefix="/login")

#############################################
########## 5. Login Manager
#############################################
# Tables
class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True)
	given_name = db.Column(db.String(255), unique=True)
	family_name = db.Column(db.String(255), unique=True)

class OAuth(db.Model, OAuthConsumerMixin):
	user_id = db.Column(db.Integer, db.ForeignKey(User.id))
	user = db.relationship(User)

# Setup login manager
login_manager = LoginManager()
login_manager.login_view = 'google.login'

# User loader
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# Setup SQLAlchemy backend
blueprint.backend = SQLAlchemyStorage(OAuth, db.session, user=current_user)

# create/login local user on successful OAuth login
@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
	if not token:
		print("Failed to log in with Google.")
		return False

	resp = blueprint.session.get("/oauth2/v2/userinfo")
	if resp.ok:
		response = resp.json()
		email = response["email"]
		query = User.query.filter_by(email=email)
		try:
			user = query.one()
		except:  # NoResultFound
			# create a user
			user = User(email=email, given_name=response.get("given_name"), family_name=response.get("family_name"))
			db.session.add(user)
			db.session.commit()
		login_user(user)
		flash("Successfully signed in with Google")
	else:
		print("Failed to fetch user info from Google.")
		return False

# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, error, error_description=None, error_uri=None):
	msg = (
		"OAuth error from {name}! "
		"error={error} description={description} uri={uri}"
	).format(
		name=blueprint.name,
		error=error,
		description=error_description,
		uri=error_uri,
	)
	flash(msg, category="error")

# Logout handler
@app.route("/logout")
@login_required
def logout():
	logout_user()
	flash("You have logged out")
	return redirect(url_for("index"))

# hook up extensions to app
db.init_app(app)
login_manager.init_app(app)

# Create
# with app.app_context():
# 	db.create_all()
# 	db.session.commit()
# 	print("Database tables created")

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
@app.route('/')
def index():

	# Redirect user
	# if current_user.is_authenticated:
		# return redirect(url_for('dashboard'))
	# else:
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

@app.route('/analyze')
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

@app.route('/analyze/published_data')
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

@app.route('/analyze/search')
def search_data():

	# Get Search Parameters
	q = request.args.get('q', 'cancer')
	min_samples = request.args.get('min_samples', 6)
	max_samples = request.args.get('max_samples', '70')
	max_samples = 500 if max_samples == '70' else max_samples
	sortby = request.args.get('sortby', 'new')
	organism = request.args.get('organism', 'all')
	organisms = [x for x in ['Human', 'Mouse'] if organism == 'all' or x == organism.title()]
	page = int(request.args.get('page', '1'))

	# Get counts
	dataset_nr = pd.read_sql_query('SELECT COUNT(DISTINCT dataset_accession) FROM dataset_v6', engine).iloc[0,0]
	sample_nr = pd.read_sql_query('SELECT COUNT(DISTINCT sample_accession) FROM sample_v6', engine).iloc[0,0]

	###
	# Search database
	query_dataframe = Q.searchDatasets(session=Session(), tables=tables, min_samples=min_samples, max_samples=max_samples, organisms=organisms, sortby=sortby, q=q)

	# Filter dataset
	nr_results = len(query_dataframe.index)

	# GEO Search
	# if not nr_results:

		# Get GSEs
		# gse = Q.searchGEO(q)
		
		# Search
		# query_dataframe = Q.searchDatasets(session=Session(), tables=tables, min_samples=min_samples, max_samples=max_samples, organisms=organisms, sortby=sortby, gse=gse)

		# Number of results
		# nr_results = len(query_dataframe.index)

	# Prepare queries to display
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
		h = lambda x: '<span class="highlight">{}</span>'.format(x) if len(x) > 3 else x
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

@app.route('/analyze/tools', methods=['GET', 'POST'])
def add_tools():

	# Check if dataset has been selected
	if request.args.get('uid') or request.form.get('gse-gpl') or request.form.get('gtex-samples-1'):

		# Get dataset information from request
		if request.args.get('uid'):
			selected_data = {'uid': request.args.get('uid'), 'source': 'upload'}
			# Check if dataset is private; if it is, abort
			session = Session()
			dataset = session.query(tables['user_dataset']).filter(tables['user_dataset'].columns['dataset_uid'] == selected_data['uid']).first()
			session.close()
			if current_user.get_id() != '3':
				if not dataset or dataset._asdict()['deleted'] or (dataset._asdict()['private'] and dataset._asdict()['user_fk'] != (int(current_user.get_id()) if current_user.get_id() else None)):
					return abort(404)
		elif request.form.get('gse-gpl'):
			selected_data = {'gse': request.form.get('gse-gpl').split('-')[0], 'gpl': request.form.get('gse-gpl').split('-')[1], 'source': 'archs4'}
		elif request.form.get('gtex-samples-1'):
			selected_data = {'source': 'gtex', 'gtex-samples-1': request.form.get('gtex-samples-1'), 'gtex-samples-2': request.form.get('gtex-samples-2'), 'group_a_label': request.form.get('gtex-group-1'), 'group_b_label': request.form.get('gtex-group-2')}

		# Perform tool and section query from database
		tools, sections = [pd.read_sql_table(x, engine) for x in ['tool', 'section']]
		tools = tools[tools['display'] == True]

		# Auto select DE and Enrichr for GTEx
		if request.form.get('gtex-samples-1'):
			ix = [index for index, rowData in tools.iterrows() if rowData['tool_string'] in ['signature_table', 'enrichr', 'volcano_plot', 'go_enrichment']]
			tools.loc[ix, 'default_selected'] = 1
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

@app.route('/analyze/configure', methods=['GET', 'POST'])
def configure_analysis():

	# Get form
	f=request.form

	# Check if form has been provided
	if f:

		# Check if requires signature
		signature_tools = pd.read_sql_query('SELECT tool_string FROM tool WHERE requires_signature = 1', engine)['tool_string'].values
		requires_signature = any([x in signature_tools for x in [x for x in f.lists()][0][-1]])

		# Signature generation
		if requires_signature and not f.get('source') == 'gtex':

			# Get metatada for processed datasets
			if 'gse' in request.form.keys():

				# Perform database query
				session = Session()
				db_query = session.query(
						tables['sample_v6'].columns['sample_accession'].label('accession'),
						tables['sample_metadata_v6'].columns['variable'], \
						tables['sample_metadata_v6'].columns['value']) \
					.join(tables['dataset_v6']) \
					.join(tables['sample_metadata_v6']) \
					.filter(tables['dataset_v6'].columns['dataset_accession'] == request.form.get('gse')).all()
				session.close()

				# Read sample dataframe
				sample_dataframe = pd.DataFrame(db_query).pivot(index='accession', columns='variable',values='value').reset_index()
				
				# Remove columns with constant values
				sample_dataframe = sample_dataframe[[col for col, colData in sample_dataframe.iteritems() if len(colData.unique()) > 1]]

			# Get metadata for user-submitted dataset
			else:

				# Perform database query
				session = Session()
				db_query = session.query(
						tables['user_sample'].columns['sample_name'].label('sample'),
						tables['user_sample_metadata'].columns['variable'], \
						tables['user_sample_metadata'].columns['value']) \
					.join(tables['user_dataset']) \
					.join(tables['user_sample_metadata']) \
					.filter(tables['user_dataset'].columns['dataset_uid'] == request.form.get('uid')).all()
				session.close()

				# Read sample dataframe
				sample_dataframe = pd.DataFrame(db_query).pivot(index='sample', columns='variable', values='value').reset_index()
		
			# Return result
			return render_template('analyze/configure_signature.html', f=f, sample_dataframe=sample_dataframe)

		else:

			# Get tool query
			tools = [value for value, key in zip(f.listvalues(), f.keys()) if key == 'tool'][0]
			session = Session()
			db_query = session.query(
					tables['tool'].columns['tool_name'], \
					tables['tool'].columns['tool_string'], \
					tables['tool'].columns['tool_description'], \
					tables['parameter'].columns['parameter_name'], \
					tables['parameter'].columns['parameter_string'], \
					tables['parameter'].columns['parameter_description'], \
					tables['parameter_value'].columns['value'], \
					tables['parameter_value'].columns['default']) \
				.outerjoin(tables['parameter']) \
				.outerjoin(tables['parameter_value']) \
				.filter(tables['tool'].columns['tool_string'].in_(tools)).all()
			session.close()
			p = pd.DataFrame(db_query).set_index(['tool_string'])#pd.read_sql_query('SELECT tool_name, tool_string, tool_description, parameter_name, parameter_description, parameter_string, value, `default` FROM tool t LEFT JOIN parameter p ON t.id=p.tool_fk LEFT JOIN parameter_value pv ON p.id=pv.parameter_fk WHERE t.tool_string IN {}'.format(tool_query_string), engine).set_index(['tool_string'])#.set_index(['tool_name', 'parameter_name', 'parameter_description', 'parameter_string'])
			
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

@app.route('/analyze/results', methods=['GET', 'POST'])
def generate_notebook():

	# Check if form has been provided
	if request.form:

		# Get form
		d = {key:value if len(value) > 1 else value[0] for key, value in request.form.lists()}

		# Get parameters and groups
		p = {x:{} for x in d['tool']} if isinstance(d['tool'], list) else {d['tool']: {}}
		g = {x:[] for x in ['a', 'b', 'none']}
		for key, value in d.items():
			if key not in ['sample-table_length', 'gtex-samples-1', 'gtex-samples-2', 'gtex-group-1', 'gtex-group-2', 'static_plots']:
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
					"A": {"name": d.get('group_a_label', ''), "samples": d['gtex-samples-1'].split(',')},
					"B": {"name": d.get('group_b_label', ''), "samples": d['gtex-samples-2'].split(',')}
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
			'terms': tags,
			'user_id': current_user.get_id()
		}

		# Get tools
		tools = pd.read_sql_query('SELECT tool_string, tool_name FROM tool', engine).set_index('tool_string').to_dict()['tool_name']
		selected_tools = [tools[x['tool_string']] for x in c['tools']]

		# Estimated wait time
		wait_times = pd.read_sql_query('SELECT time, count(tool_fk) AS tools FROM notebook n LEFT JOIN notebook_tool nt ON n.id=nt.notebook_fk GROUP BY n.id HAVING time > 0 AND tools ='+str(len(p)), engine)['time']
		expected_time = int(np.ceil(np.percentile(wait_times, 90)/60))
		
		# Return result
		return render_template('analyze/results.html', notebook_configuration=json.dumps(c), notebook_configuration_dict=c, selected_tools=selected_tools, dev=dev, expected_time=expected_time)
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

@app.route('/notebook/<notebook_uid>')
def view_notebook(notebook_uid):

	# Get notebook data
	session = Session()
	db_query = session.query(tables['notebook'].columns['notebook_title'], tables['notebook'].columns['version'], tables['notebook'].columns['user_fk'], tables['notebook'].columns['private'], tables['notebook'].columns['deleted']) \
						.filter(tables['notebook'].columns['notebook_uid'] == notebook_uid)
	query_results = [x._asdict() for x in db_query.all()]
	session.close()

	# Check if notebook has been found
	if len(query_results) == 1:

		# Get notebook data
		notebook_dict = query_results[0]

		# Check privacy settings
		if not notebook_dict['deleted'] and ((notebook_dict['private'] and current_user.get_id() and int(current_user.get_id()) in [notebook_dict['user_fk'], 3]) or (not notebook_dict['private'])):
			
			# Whether to display HTTPS (Clustergrammer and L1000FWD only support HTTPS iframe in version >=v0.8)
			version = float('.'.join(notebook_dict['version'][1:].split('.')[:2]))
			https = version > 0.7 or version < 0.2

			# Get Nbviewer URL and Title
			nbviewer_url = 'https://nbviewer.jupyter.org/urls/storage.googleapis.com/jupyter-notebook-generator/{notebook_uid}/{notebook_dict[notebook_title]}.ipynb'.format(**locals())

			# Replace HTTPS
			if not https:
				nbviewer_url = nbviewer_url.replace('https://', 'http://')

			# Return result
			return render_template('analyze/notebook.html', nbviewer_url=nbviewer_url, title=notebook_dict['notebook_title'], https=https, private=notebook_dict['private'])

		else:
			abort(404)

	# Return 404
	else:
		abort(404)

#############################################
########## 11. GTEx Interface
#############################################
### Allows users to generate notebooks from GTEx data.
### Links to: .
### Accessible from: .

@app.route('/gtex')
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

@app.route('/api/ontology')
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

@app.route('/api/gtex', methods=['POST'])
def gtex_api():

	# Read data
	gtex_data = pd.read_sql_query('SELECT "" AS checkbox, AGE AS Age, SMTSD AS Tissue, SEX AS Gender, SAMPID AS id FROM gtex_metadata', engine).replace('1', 'Male').replace('2', 'Female').to_dict(orient='records')

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

@app.route('/upload')
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

@app.route('/upload/table', methods=['GET', 'POST'])
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

@app.route('/upload/reads', methods=['GET', 'POST'])
def upload_reads():

	# Alignment settings
	if request.args.get('upload'):

		# Get upload UID
		upload_uid = request.args.get('upload')

		# Redirect if UID is short
		if len(upload_uid) < 11:
			abort(404)
		
		# Else
		else:

			# Find alignment
			session = Session()
			upload_user_id = session.query(tables['fastq_upload'].columns['user_fk']).filter(tables['fastq_upload'].columns['upload_uid'] == upload_uid).first()
			upload_user_id = upload_user_id[0] if upload_user_id else None
			session.close()

			# Check if user matches
			if (upload_user_id and ((current_user.get_id() and int(current_user.get_id()) in (upload_user_id, 3))) or (not upload_user_id)):

				# Get samples
				req =  urllib.request.Request('https://amp.pharm.mssm.edu/charon/files?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}'.format(**os.environ))
				uploaded_files = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))['filenames']
				samples = [x for x in uploaded_files if x.startswith(upload_uid) and (x.endswith('.fastq.gz') or x.endswith('.fq.gz'))]

				### If UID doesn't exist in the database and files are matched, upload UID and files to database
				if len(samples):
					# RM.uploadToDatabase(upload_uid, samples, session = Session(), tables=tables, user_id=current_user.get_id()) ### move this to uploading reads
					return render_template('upload/align_reads.html', upload_uid=upload_uid, samples=samples)
				else:
					abort(404)
			else:
				abort(404)

	# Alignment status
	elif request.args.get('alignment'):

		# Get form data
		alignment_uid = request.args.get('alignment')

		# Find alignment
		session = Session()
		alignment_data = session.query(tables['fastq_upload'].columns['user_fk'], tables['fastq_alignment'].columns['deleted']).join(tables['fastq_alignment']).filter(tables['fastq_alignment'].columns['alignment_uid'] == alignment_uid).first()
		# alignment_user_id = session.query(tables['fastq_upload'].columns['user_fk']).join(tables['fastq_alignment']).filter(tables['fastq_alignment'].columns['alignment_uid'] == alignment_uid).first()
		alignment_user_id = alignment_data.user_fk if alignment_data else None
		session.close()

		# Check if user matches
		if (not alignment_data.deleted) and ((alignment_user_id and ((current_user.get_id() and int(current_user.get_id()) in (alignment_user_id, 3))) or (not alignment_user_id))):

			# Get jobs
			print('performing request...')
			req =  urllib.request.Request('https://amp.pharm.mssm.edu/cloudalignment/progress?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}'.format(**os.environ))
			job_dataframe = pd.DataFrame(json.loads(urllib.request.urlopen(req).read().decode('utf-8'))).T
			print('done!')
			jobs = job_dataframe.loc[[index for index, rowData in job_dataframe.iterrows() if rowData['outname'].startswith(alignment_uid)]].to_dict(orient='records')
			if len(jobs):
				failed = any([x['status'] == 'failed' for x in jobs])

				### Add job to database, adding foreign key for upload
				# RM.uploadJob(jobs, session=Session(), tables=tables)

				return render_template('upload/alignment_status.html', alignment_uid=alignment_uid, jobs=jobs, failed=failed)

			else:
				abort(404)
		else:
			abort(404)

	# Preview table
	elif request.args.get('table'):

		return render_template('upload/alignment_preview.html', alignment_uid=request.args.get('table'))

	# Annotate
	elif request.form.get('expression'):

		# Get form
		f = request.form.to_dict()

		# Get samples for group table
		samples = json.loads(f['expression'])['columns']
		samples.sort()

		# Get groups
		groups = [x for x in set([common_start(x, y) for x, y in itertools.combinations(samples, 2)]) if len(x)]
		groups.sort(key=len)

		# Assign groups
		matches = {sample: [group for group in groups if group in sample] for sample in samples}
		sample_groups = [{'sample': sample, 'group': matches[sample][-1] if len(matches[sample]) else ''} for sample in samples]

		# Get alignment species, if from FASTQ
		if f.get('alignment_uid'):
			# Find species
			session = Session()
			alignment_data = session.query(tables['fastq_alignment']).filter(tables['fastq_alignment'].columns['alignment_uid'] == f.get('alignment_uid')).first()
			alignment_species = alignment_data.species if alignment_data else None
			session.close()
			f['reference_genome'] = alignment_species.replace('hs', 'GRCh38 human').replace('mm', 'GRCh38 mouse')
			
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

@app.route('/api/upload/dataframe', methods=['POST'])
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

@app.route('/api/upload/table', methods=['POST'])
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
	TM.uploadToDatabase(data, dataset_uid, engine, user_id=current_user.get_id(), dataset_title=data.get('dataset_title', 'Untitled Dataset'), alignment_uid=data.get('alignment_uid'), session=Session(), tables=tables)

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

@app.route('/api/upload/example', methods=['POST'])
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

@app.route('/api/upload/launch_alignment', methods=['GET', 'POST'])
def launch_alignment_api():

	# Get form
	alignment_settings = request.form.to_dict()
	# Get sample files
	if alignment_settings['sequencing-type'] == 'single-end':
		samples = [{'outname': value.rsplit('.', 2)[0], 'file1': value, 'file2': None} for key, value in alignment_settings.items() if key.startswith('file')]
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

		# Get URL parameters
		params = '&'.join(['{key}={value}'.format(**locals()) for key, value in sample.items() if value])+'&organism='+alignment_settings['organism']
		url = "https://amp.pharm.mssm.edu/cloudalignment/createjob?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}&".format(**os.environ)+params
		# Launch alignment jobs
		req =  urllib.request.Request(urllib.parse.quote(url, safe=':/&.?='))
		# req =  urllib.request.Request(url.replace(' ', '%20'))
		resp = urllib.request.urlopen(req).read().decode('utf-8')
		# print(resp)

	# Upload to database
	RM.uploadAlignmentJob(alignment_uid=alignment_uid, upload_uid=alignment_settings['upload_uid'], paired=alignment_settings.get('sequencing-type')=='paired-end', species=alignment_settings['organism'].replace('human', 'hs').replace('mouse', 'mm'), alignment_title=alignment_settings.get('alignment_title', 'FASTQ Alignment'), session=Session(), tables=tables)

	return json.dumps({'alignment_uid': alignment_uid})

#############################################
########## 5. Merge Counts API
#############################################
### Merges counts from Amazon S3 to a pandas dataframe based on a dataset UID.
### Input: a JSON-formatted string containing one key: alignment_uid. It specifies the UID of the count matrix to generate.
### Output: a JSON-formatted string generated using pd.to_dict(orient='split')
### Called by: upload_reads().

@app.route('/api/upload/merge_counts', methods=['GET', 'POST'])
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
		req =  urllib.request.Request('https://s3.amazonaws.com/biodos/c095573dc866f2db2cd39862ad89f074/'+sample.replace(' ', '%20'))

		# Build dataframe
		counts = pd.read_table(StringIO(urllib.request.urlopen(req).read().decode('utf-8')), header=None, names=['gene_symbol', 'counts'])
		counts['counts'] = counts['counts'].astype(int)
		counts['sample'] = sample_name
		
		# Append
		results.append(counts)

	# Create dataframe
	count_dataframe = pd.concat(results).pivot_table(index='gene_symbol', columns='sample', values='counts')

	# Get QC info
	qc_infos = [x for x in uploaded_files if x.startswith(alignment_uid) and x.endswith('_qc.tsv')]

	# Initialize dict
	qc_results = {}

	# Read
	for qc_info in qc_infos:

		# Get sample name
		sample_name = qc_info[(len(alignment_uid)+1)*2:-len('-hs_qc.tsv')]

		# Get counts from S3
		req =  urllib.request.Request('https://s3.amazonaws.com/biodos/c095573dc866f2db2cd39862ad89f074/'+qc_info.replace(' ', '%20'))

		# Build dataframe
		qc = urllib.request.urlopen(req).read().decode('utf-8')
		
		# Get summary
		qc_summary = [x for x in qc.split('\n') if x.startswith('[quant] processed')]
		
		# Extract
		if len(qc_summary) == 1:
			qc_split = qc_summary[0].split(' ')
			qc_results[sample_name] = {'processed': qc_split[2], 'pseudoaligned': qc_split[4]}
		else:
			qc_results[sample_name] = {}

	# Return
	return json.dumps({'counts': count_dataframe.to_dict(orient='split'), 'qc': qc_results})

#############################################
########## 7. Query Elysium API
#############################################
### Queries Elysium.
### Input: JSON requesting information on files, progress.
### Output: JSON.
### Called by: several routes.

@app.route('/api/elysium', methods=['GET'])
def elysium_api():

	# Get data
	endpoint = request.args.get('request_type')

	# Set parameters
	if endpoint == 'signpolicy':

		# Build url
		url = 'https://amp.pharm.mssm.edu/charon/{endpoint}?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}'.format(**os.environ, **locals())

		# Read request
		data = urllib.request.urlopen(urllib.request.Request(url)).read().decode('utf-8')

	elif endpoint == 'progress':

		# Build url
		url = 'https://amp.pharm.mssm.edu/cloudalignment/{endpoint}?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}'.format(**os.environ, **locals())

		# Get alignment UID
		alignment_uid = request.args.get('alignment_uid')

		# Check
		if isinstance(alignment_uid, str) and len(alignment_uid) == 11:

			# Get job dataframe
			job_dataframe = pd.DataFrame(json.loads(urllib.request.urlopen(urllib.request.Request(url)).read().decode('utf-8'))).T
			
			# Get jobs
			jobs = job_dataframe.loc[[index for index, rowData in job_dataframe.iterrows() if rowData['outname'].startswith(alignment_uid)]].to_dict(orient='records')

			# Convert to JSON
			data = json.dumps(jobs)

		else:
			raise ValueError('Unsupported alignment id.')

	else:
		raise ValueError('Endpoint not supported.')

	# Return
	return data

#############################################
########## 6. Upload Reads API
#############################################
### Uploads the upload UID to the database.
### Input: upload UID.
### Output: None.
### Called by: upload_reads().

@app.route('/api/upload/upload_reads', methods=['GET', 'POST'])
def upload_reads_api():

	# Get data
	r = request.json

	# Open database session
	session = Session()

	try:
		# Insert upload UID
		upload_id = session.execute(tables['fastq_upload'].insert().values([{'upload_uid': r['upload_uid'], 'user_fk': current_user.get_id()}])).lastrowid

		# Upload samples
		session.execute(tables['fastq_file'].insert().values([{'filename': sample, 'fastq_upload_fk': upload_id} for sample in r['filenames']]))

		# Commit
		session.commit()
	except:
		pass

	# Close session
	session.close()

	# Return
	return json.dumps({'result': 'success'})

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

@app.route('/contribute', methods=['GET', 'POST'])
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

@app.route('/docker')
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

@app.route('/api/notebook/<notebook_uid>', methods=['GET'])
def notebook_api(notebook_uid):

	# Open session
	session = Session()
	
	# Initialize database query
	db_query_results = session.query(tables['notebook']).filter(tables['notebook'].columns['notebook_uid'] == notebook_uid).all()

	# Close session
	session.close()

	# If results
	if len(db_query_results):
		notebook_data = db_query_results[0]._asdict()
		notebook_data['date'] = notebook_data['date'].strftime('%b %d, %Y')
		if not notebook_data['deleted']:
			notebook_data['download_url'] = 'https://storage.googleapis.com/jupyter-notebook-generator/{notebook_uid}/{notebook_title}.ipynb'.format(**notebook_data)
		del notebook_data['notebook_configuration']
		del notebook_data['id']
		del notebook_data['user_fk']
		del notebook_data['deleted']
		del notebook_data['private']
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

@app.route('/help')
def help():
	with open('app/static/help/sections.json') as openfile:
		categories = json.load(openfile)
	return render_template('help.html', categories=categories, entry_point=entry_point)

#############################################
########## 2. Example Dataset
#############################################
### Example dataset.
### Accessible from: analyze().

@app.route('/analyze/example')
def example():

	# Select dataset
	dataset_accession = 'GSE88741'
	dataset = pd.read_sql_query('SELECT platform_accession, dataset_accession, dataset_title, summary, date, count(*) AS nr_samples, organism FROM dataset_v6 d LEFT JOIN sample_v6 s ON d.id=s.dataset_fk LEFT JOIN platform_v6 p ON p.id=s.platform_fk WHERE dataset_accession = "{}"'.format(dataset_accession), engine).drop_duplicates().T.to_dict()[0]
	# dataset['date'] = dataset['date'].strftime('%b %d, %Y')
	return render_template('analyze/example.html', dataset=dataset)

##################################################
########## 3.2 APIs
##################################################

#############################################
########## 1. Statistics
#############################################

@app.route('/api/stats')
def stats_api():
	
	# Get object
	obj = request.args.get('obj')

	# Check object
	if obj in ['notebook', 'tool', 'dataset_v6', 'user_dataset', 'fastq_file', 'sample_v6']:

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
########## 6. User Routes
#######################################################
#######################################################
##### Handles user account-related templates.

##################################################
########## 3.1 Dashboard
##################################################

#############################################
########## 1. User Dashboard
#############################################

@app.route('/dashboard')
def dashboard():
	if not current_user.is_authenticated:
		return redirect(url_for('google.login'))
	else:

		# Get User ID
		user_id = current_user.get_id()

		# Start session
		session = Session()

		# Get datasets
		datasets = session.query(tables['user_dataset'], func.count(tables['user_sample'].columns['id']).label('samples')).join(tables['user_sample']).filter(and_(tables['user_dataset'].columns['user_fk'] == user_id, tables['user_dataset'].columns['deleted'] == 0)).group_by(tables['user_dataset'].columns['id']).order_by(tables['user_dataset'].columns['date'].desc()).all()

		# Get notebooks
		notebooks = session.query(tables['notebook']).filter(and_(tables['notebook'].columns['user_fk'] == user_id, tables['notebook'].columns['deleted'] == 0)).order_by(tables['notebook'].columns['date'].desc()).all()

		# Get alignment jobs
		alignments = session.query(tables['fastq_alignment']).join(tables['fastq_upload']).filter(and_(tables['fastq_upload'].columns['user_fk'] == user_id, tables['fastq_alignment'].columns['deleted'] == 0)).order_by(tables['fastq_alignment'].columns['date'].asc()).all()

		# Get statuses
		if alignments:

			# Get progress
			req =  urllib.request.Request('https://amp.pharm.mssm.edu/cloudalignment/progress?username={ELYSIUM_USERNAME}&password={ELYSIUM_PASSWORD}'.format(**os.environ))
			progress_dataframe = pd.DataFrame(json.loads(urllib.request.urlopen(req).read().decode('utf-8'))).T[['outname', 'status']]
			progress_dataframe['split'] = [x.split('-')[0] for x in progress_dataframe['outname']]
			progress_dataframe['sample_name'] = [x.split('-', 2)[-1].split('-', -1)[0] if '-' in x else '' for x in progress_dataframe['outname']]
			progress = progress_dataframe[progress_dataframe['split'].isin(alignment.alignment_uid for alignment in alignments)].groupby('split')[['sample_name', 'status']].apply(lambda x: x.sort_values('sample_name').to_dict(orient='records')).to_dict()

			# Add to alignments
			alignments = [x._asdict() for x in alignments if progress.get(x.alignment_uid)]
			for alignment in alignments:
				alignment['progress'] = progress.get(alignment['alignment_uid'])
				status_count = pd.DataFrame(alignment['progress']).groupby('status')['sample_name'].apply(list).to_dict()
				if 'failed' in status_count.keys():
					status = 'failed'
				elif 'submitted' in status_count.keys():
					status = 'submitted'
				elif 'waiting' in status_count.keys():
					status = 'pending'
				else:
					status = 'completed'
				alignment['status_count'] = status_count
				alignment['status'] = status
				alignment['progress_json'] = json.dumps(alignment['progress'])

		# Close session
		session.close()

		return render_template('user/dashboard.html', datasets=datasets, notebooks=notebooks, alignments=alignments, dev=dev)

#############################################
########## 2. Private API
#############################################

@app.route('/api/edit_object', methods=['GET', 'POST'])
def edit_object():

	# Get form data
	data = request.json#()#{'table': 'user_dataset', 'uid': 'ETnw5p01YjN', 'action': 'rename', 'title': 'New Data'}  # request.json
	print(data)

	# Get column name
	object_label = data['object_type'].replace('user_','').replace('fastq_','')

	# Start database session
	session = Session()

	# Try
	try:

		# Get object data
		object_data = session.query(tables['fastq_alignment'], tables['fastq_upload'].columns['user_fk']).join(tables['fastq_upload']).filter(tables['fastq_alignment'].columns['alignment_uid'] == data['uid']).all() if data['object_type'] == 'fastq_alignment' else session.query(tables[data['object_type']]).filter(tables[data['object_type']].columns[object_label+'_uid'] == data['uid']).all()

		# Check length
		if len(object_data):
			# Get object
			object_data = object_data[0]._asdict()

			# Check if user ID matches with owner of object
			if current_user.get_id() and object_data['user_fk'] == int(current_user.get_id()):

				# Action
				if data['action'] == 'change_privacy':

					# Find value
					private = 0 if object_data['private'] else 1

					# Set value
					session.execute(tables[data['object_type']].update().where(tables[data['object_type']].columns['id'] == object_data['id']).values({'private': private}))

					# Get response
					response = {'private': private}
					print('set to {}'.format(private))

				elif data['action'] == 'rename':

					# Set value
					session.execute(tables[data['object_type']].update().where(tables[data['object_type']].columns['id'] == object_data['id']).values({object_label+'_title': data['title']}))

					# Get response
					response = {'title': data['title']}
					print('set to {}'.format(data['title']))

				elif data['action'] == 'delete':

					# Set value
					session.execute(tables[data['object_type']].update().where(tables[data['object_type']].columns['id'] == object_data['id']).values({'deleted': 1}))

					# Get response
					response = {'deleted': True}
					print('deleted {object_type} {uid}'.format(**data))

				elif data['action'] == 'save_notes':

					# Set value
					session.execute(tables[data['object_type']].update().where(tables[data['object_type']].columns['id'] == object_data['id']).values({'notes': data['title']}))

					# Get response
					response = {'saved': True}
					print('saved notes for {object_type} {uid}'.format(**data))

				# Commit
				session.commit()

			else:
				response = {}
		else:
			response = {}

		# Response
		response = json.dumps(response)

	except:
		# Rollback
		session.close()

		# Get response
		response = jsonify({'result': 'error'})
		response.status_code = 500

		# Rollback
		session.rollback()
		raise

	# Close session
	session.close()

	return response


#######################################################
#######################################################
########## 7. Handlers
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
	
	return render_template('errors/500.html', now=datetime.utcnow()), 500

#############################################
########## 3. Notebook Generation Error
#############################################

@app.route('/error/<error_id>')
def notebook_generation_error(error_id):
	
	# Query
	session = Session()
	db_query = session.query(tables['error_log']).filter(tables['error_log'].columns['id'] == error_id).all()
	session.close()
	
	# Get results
	if len(db_query):
		error = db_query[0]._asdict()
		error['notebook_configuration'] = json.loads(error['notebook_configuration'])
		error['notebook_configuration_json'] = json.dumps(error['notebook_configuration'], indent=4)

		return render_template('errors/notebook_generation_error.html', error=error)

@app.route('/err')
def err():
	return render_template('errors/500.html', now=datetime.utcnow())

#######################################################
#######################################################
########## 7. Run App
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################
