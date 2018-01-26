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
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

##### 2. Python modules #####
import sys, os, json
import pandas as pd

##### 3. Custom modules #####
sys.path.append('static/py')
from NotebookGenerator import *

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
########## 2. Get Datasets
#############################################

@app.route(entry_point+'/api/datasets', methods=['GET', 'POST'])
def datasets():

	gse_list = json.loads(request.get_data())['gse']
	gse_string = '("'+'", "'.join(gse_list)+'")'
	sample_dataframe = pd.read_sql_query('SELECT gse, gsm, gpl, sample_title FROM series se LEFT JOIN sample sa ON se.id=sa.series_fk LEFT JOIN platform p ON p.id=sa.platform_fk WHERE gse in {}'.format(gse_string), engine, index_col='gse')
	result = {gse:{} for gse in gse_list}
	for gse in sample_dataframe.index:
		platforms = sample_dataframe.loc[gse]['gpl'].unique()
		for platform in platforms:
			result[gse][platform] = sample_dataframe.loc[gse].set_index('gpl').loc[platform].to_dict(orient='records')
	return json.dumps(result)

#######################################################
#######################################################
########## 3. Run App
#######################################################
#######################################################

#############################################
########## 1. Run
#############################################
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')