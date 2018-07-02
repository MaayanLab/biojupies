#################################################################
#################################################################
############### Notebook Generator Server #######################
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
from flask import Flask, request, render_template, Response
from flask_sqlalchemy import SQLAlchemy

##### 2. Python modules #####
import sys, os, json, time, re
import pandas as pd
import pymysql
pymysql.install_as_MySQLdb()

##### 3. Custom modules #####
sys.path.append('app/static/py')
from NotebookGenerator import *
from NotebookManager import *

#############################################
########## 2. App Setup
#############################################
##### 1. Flask App #####
# General
dev = False
entry_point = '/notebook-generator-server-dev' if dev else '/notebook-generator-server'
app = Flask(__name__, static_url_path=os.path.join(entry_point, 'app/static'))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']#+'-dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
engine = db.engine

##### 2. Variables #####
# Latest library version
latest_library_version = os.environ['LIBRARY_VERSION']

#######################################################
#######################################################
########## 2. Server
#######################################################
#######################################################

#############################################
########## 1. Home
#############################################

@app.route(entry_point, methods=['GET', 'POST'])
def index():
	return render_template('index.html')

#############################################
########## 2. Generate API
#############################################

@app.route(entry_point+'/api/generate', methods=['GET', 'POST'])
def generate():

	# Get tool metadata
	tool_metadata = pd.read_sql_table('tool', engine).set_index('tool_string').to_dict(orient='index')
	core_script_metadata = pd.read_sql_table('core_scripts', engine).set_index('option_string').to_dict(orient='index')
	annotations = {'tools': tool_metadata, 'core_options': core_script_metadata}
	print('generating notebook...')

	# Set development
	development = os.environ['DEVELOPMENT'] == 'True'
	try:
		### Development
		if development or request.method == 'GET':

			# Open example.json
			with open('example.json', 'r') as openfile:
				notebook_configuration = json.loads(openfile.read())

			# Generate, Execute and Convert to HTML
			notebook = generate_notebook(notebook_configuration, annotations)
			notebook = execute_notebook(notebook, execute=True, to_html=True)
		
			# Return
			return notebook

		### Production
		else:
			# Get Configuration
			notebook_configuration = request.json
			# with open('example.json', 'r') as openfile:
			# 	notebook_configuration = json.loads(openfile.read())

			# Check if notebook exists
			# matching_notebook = pd.read_sql_query("SELECT * FROM notebooks WHERE notebook_configuration = '{}'".format(json.dumps(notebook_configuration)), engine).to_dict(orient='records')
			matching_notebook = pd.read_sql_query("SELECT * FROM notebook WHERE notebook_configuration = '{}'".format(json.dumps(notebook_configuration)), engine).to_dict(orient='records')

			# Return existing notebook
			if len(matching_notebook):

				# Get URL
				notebook_uid = matching_notebook[0]['notebook_uid']

			# Generte new notebook
			else:

				# Generate and Execute
				notebook = generate_notebook(notebook_configuration, annotations)
				notebook, time = execute_notebook(notebook)

				# Get URL
				notebook_uid = upload_notebook(notebook, notebook_configuration, time, engine)

			# Return
			return json.dumps({'notebook_uid': notebook_uid, 'notebook_url': 'http://amp.pharm.mssm.edu/biojupies/notebook/'+notebook_uid})
			# return json.dumps({'notebook_uid': notebook_uid, 'notebook_url': 'http: // nbviewer.jupyter.org/urls/'+notebook_url.split(': //')[-1]})

	except Exception as e:

		# Raise
		if development:
			raise
		else:

			# Get Configuration
			notebook_configuration = request.json

			# Get error message
			ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

			# Get response
			error_response = log_error(notebook_configuration, ansi_escape.sub('', str(e)), annotations, engine)

			return error_response

#######################################################
#######################################################
########## 3. Extension API
#######################################################
#######################################################

#############################################
########## 1. Version API
#############################################

@app.route(entry_point+'/api/version', methods=['GET', 'POST'])
def version():
	return json.dumps({'latest_library_version': latest_library_version})

#############################################
########## 2. Samples API
#############################################

@app.route(entry_point+'/api/samples', methods=['GET', 'POST'])
def samples():

	# Get GSE
	gse_list = json.loads(request.get_data())['gse']
	
	# Get Sample Dataframe
	gse_string = '("'+'", "'.join(gse_list)+'")'
	# sample_dataframe = pd.read_sql_query('SELECT gse, gsm, gpl, sample_title FROM series se LEFT JOIN sample sa ON se.id=sa.series_fk LEFT JOIN platform p ON p.id=sa.platform_fk WHERE gse in {}'.format(gse_string), engine, index_col='gse')
	sample_dataframe = pd.read_sql_query('SELECT dataset_accession AS gse, sample_accession AS gsm, platform_accession AS gpl, sample_title FROM dataset d LEFT JOIN sample_new s ON d.id=s.dataset_fk LEFT JOIN platform_new p ON p.id=s.platform_fk WHERE dataset_accession in {}'.format(gse_string), engine, index_col='gse')

	# Initialize result dict
	result = {gse:{} for gse in gse_list}

	# Loop through series
	for gse in sample_dataframe.index.unique():

		# Check if series has over 3 samples
		if len(sample_dataframe.loc[gse].index) > 3:
			platforms = sample_dataframe.loc[gse]['gpl'].unique()

			# Add platforms
			for platform in platforms:
				if len(sample_dataframe.loc[gse].set_index('gpl').loc[platform].index) > 3:
					result[gse][platform] = sample_dataframe.loc[gse].set_index('gpl').loc[platform].sort_values('sample_title').to_dict(orient='records')

	# Return
	return json.dumps(result)

#############################################
########## 3. Tools API
#############################################

@app.route(entry_point+'/api/tools', methods=['GET', 'POST'])
def tools():

	# Get data
	tool_dict = pd.read_sql_query('SELECT id, tool_string, tool_name, tool_description, default_selected, requires_signature FROM tool', engine, index_col='id').to_dict(orient='index')
	parameter_dataframe = pd.read_sql_query('SELECT * FROM parameter', engine, index_col='tool_fk')
	parameter_value_dataframe = pd.read_sql_query('SELECT * FROM parameter_value', engine, index_col='parameter_fk').drop('id', axis=1)

	# Add parameter values
	parameter_value_dict = {x:pd.DataFrame(parameter_value_dataframe).loc[x].to_dict(orient='records') for x in parameter_value_dataframe.index.unique()}
	parameter_dataframe['values'] = [parameter_value_dict.get(x, []) for x in parameter_dataframe['id']]
	parameter_dataframe.drop('id', axis=1, inplace=True)

	# Add parameters
	parameter_dict = {x: (parameter_dataframe.loc[x] if isinstance(parameter_dataframe.loc[x], pd.DataFrame) else parameter_dataframe.loc[x].to_frame().T).to_dict(orient='records') for x in parameter_dataframe.index.unique()}
	for tool_id, tool_data in tool_dict.items():
		tool_data['parameters'] = parameter_dict.get(tool_id, [])

	# Reindex
	tool_dict = pd.DataFrame(tool_dict).T.set_index('tool_string', drop=False).to_dict(orient='index')

	# Get sections
	statement = 'SELECT s.id, section_name, tool_string FROM section s LEFT JOIN tool t ON s.id=t.section_fk'
	if not dev:
		statement += ' WHERE t.display = 1'
	section_dict = pd.read_sql_query(statement, engine).groupby(['id', 'section_name']).aggregate(lambda x: tuple(x)).reset_index().drop('id', axis=1).to_dict(orient='records')

	return json.dumps({'tools': tool_dict, 'sections': section_dict})

#######################################################
#######################################################
########## Run App
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')
