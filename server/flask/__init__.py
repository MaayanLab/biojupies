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
from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

##### 2. Python modules #####
import sys, os, json, time
import pandas as pd
import pymysql
pymysql.install_as_MySQLdb()

##### 3. Custom modules #####
sys.path.append('static/py')
from NotebookGenerator import *
from NotebookManager import *

#############################################
########## 2. App Setup
#############################################
##### 1. Flask App #####
# General
entry_point = '/notebook-generator-server'
app = Flask(__name__, static_url_path=os.path.join(entry_point, 'static'))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
engine = db.engine

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

import nbformat as nbf

@app.route(entry_point+'/api/generate', methods=['GET', 'POST'])
def generate():

	# Get tool metadata
	tool_metadata = pd.read_sql_table('tool', engine).set_index('tool_string').to_dict(orient='index')

	# Set development
	development = True
	if development:
		### Development
		# Open example.json
		with open('../example.json', 'r') as openfile:
			notebook_configuration = json.loads(openfile.read())

		# Generate, Execute and Convert to HTML
		notebook = generate_notebook(notebook_configuration, tool_metadata)
		notebook = execute_notebook(notebook, execute=True,to_html=True)
	
		# Return
		return notebook

	else:
		### Production
		# Get Configuration
		notebook_configuration = request.json

		# Generate and Execute
		notebook = generate_notebook(notebook_configuration, tool_metadata)
		notebook = execute_notebook(notebook)

		# Get URL
		notebook_url = upload_notebook(notebook, notebook_configuration['notebook']['title'])

		# Return
		return json.dumps({'notebook_url': 'http://nbviewer.jupyter.org/urls/'+notebook_url.split('://')[-1]})

#######################################################
#######################################################
########## 3. Extension API
#######################################################
#######################################################

#############################################
########## 1. Samples API
#############################################

@app.route(entry_point+'/api/samples', methods=['GET', 'POST'])
def samples():

	# Get GSE
	gse_list = json.loads(request.get_data())['gse']
	
	# Get Sample Dataframe
	gse_string = '("'+'", "'.join(gse_list)+'")'
	sample_dataframe = pd.read_sql_query('SELECT gse, gsm, gpl, sample_title FROM series se LEFT JOIN sample sa ON se.id=sa.series_fk LEFT JOIN platform p ON p.id=sa.platform_fk WHERE gse in {}'.format(gse_string), engine, index_col='gse')

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
########## 2. Tools API
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
	section_dict = pd.read_sql_query('SELECT s.id, section_name, tool_string FROM section s LEFT JOIN tool t ON s.id=t.section_fk', engine).groupby(['id', 'section_name']).aggregate(lambda x: tuple(x)).reset_index().drop('id', axis=1).to_dict(orient='records')

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