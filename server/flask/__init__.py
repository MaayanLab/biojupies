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
import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

##### 2. Python modules #####
import sys, os, json, time
import pandas as pd

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

@app.route(entry_point+'/api/generate', methods=['GET', 'POST'])
def generate():

	# Generate
	# notebook_configuration = json.loads(request.args.get('data'))
	with open('../example.json', 'r') as openfile:
		notebook_configuration = json.loads(openfile.read())
	notebook = generate_notebook(notebook_configuration)

	# Get URL url = 'http://nbviewer.jupyter.org/urls/'+notebook_url.split('://')[-1]
	notebook_string = execute_notebook(notebook)
	notebook_url = upload_notebook(notebook_string, notebook_configuration['notebook']['title'])

	# Return
	return notebook_url

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
	# gse_list = ['GSE65926', 'GSE109694', 'GSE107530', 'GSE109653', 'GSE78497', 'GSE99088', 'GSE107195', 'GSE106989', 'GSE107307', 'GSE109528', 'GSE109522', 'GSE109490', 'GSE109483', 'GSE103021', 'GSE102616', 'GSE103790', 'GSE95132', 'GSE95130', 'GSE91061', 'GSE93628', 'GSE93627', 'GSE100990', 'GSE108753', 'GSE106261', 'GSE95656', 'GSE105083', 'GSE93911', 'GSE106901', 'GSE107542', 'GSE109463', 'GSE109418', 'GSE101665', 'GSE108763', 'GSE109373', 'GSE95013', 'GSE102721', 'GSE102727', 'GSE107801', 'GSE107915', 'GSE102937', 'GSE103471', 'GSE109279', 'GSE100684', 'GSE106423', 'GSE93709', 'GSE99233', 'GSE74230', 'GSE97450', 'GSE98183', 'GSE95542', 'GSE104552', 'GSE101480', 'GSE109072', 'GSE97037', 'GSE90830', 'GSE100076', 'GSE100075', 'GSE99149', 'GSE103876', 'GSE103350', 'GSE109028', 'GSE86855', 'GSE108883', 'GSE107096', 'GSE108308', 'GSE96634', 'GSE104309', 'GSE104308', 'GSE99808', 'GSE107670', 'GSE93309', 'GSE108811', 'GSE108757', 'GSE103907', 'GSE107196', 'GSE100092', 'GSE80776', 'GSE106107', 'GSE97993', 'GSE108495', 'GSE97389', 'GSE95478', 'GSE93069', 'GSE90153', 'GSE107053', 'GSE107117', 'GSE80777', 'GSE67934', 'GSE86280', 'GSE99867', 'GSE106844', 'GSE84820', 'GSE104633', 'GSE103934', 'GSE93904', 'GSE94375', 'GSE94373', 'GSE94369', 'GSE90519', 'GSE98091', 'GSE104264', 'GSE103602', 'GSE75743', 'GSE75742', 'GSE75741', 'GSE79988', 'GSE100465', 'GSE100464', 'GSE98871', 'GSE102305', 'GSE99626', 'GSE80619', 'GSE80358', 'GSE107762', 'GSE88830', 'GSE82142', 'GSE81925', 'GSE97408', 'GSE97443', 'GSE108528', 'GSE92943', 'GSE106330', 'GSE102753', 'GSE94243', 'GSE89799', 'GSE108391', 'GSE104054', 'GSE101297', 'GSE72403', 'GSE107518', 'GSE107590', 'GSE98760', 'GSE86065', 'GSE108367', 'GSE108334', 'GSE88741', 'GSE107470', 'GSE94528', 'GSE100530', 'GSE108322', 'GSE78957', 'GSE94999', 'GSE95011', 'GSE100276', 'GSE85731', 'GSE100385', 'GSE106291', 'GSE96035', 'GSE108140', 'GSE81084', 'GSE102762', 'GSE107289', 'GSE107281', 'GSE108111', 'GSE107395', 'GSE95294', 'GSE95293', 'GSE108041', 'GSE108013', 'GSE91062', 'GSE87187', 'GSE87189', 'GSE92344', 'GSE98050', 'GSE95541', 'GSE95537', 'GSE103895', 'GSE98496', 'GSE103850', 'GSE101997', 'GSE101995', 'GSE101994', 'GSE108004', 'GSE108003', 'GSE106273', 'GSE87514', 'GSE87511', 'GSE101972', 'GSE107848', 'GSE64082', 'GSE92322', 'GSE107030', 'GSE104294', 'GSE104855', 'GSE106605', 'GSE107783', 'GSE107735', 'GSE95374', 'GSE67807', 'GSE67863', 'GSE107653', 'GSE105166', 'GSE105138', 'GSE105137', 'GSE100797', 'GSE85432', 'GSE85431', 'GSE107581', 'GSE107601', 'GSE107560', 'GSE107559']
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