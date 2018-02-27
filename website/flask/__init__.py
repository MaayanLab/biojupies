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
import sys, os, json
import pandas as pd
import pymysql
pymysql.install_as_MySQLdb()

##### 3. Custom modules #####

#############################################
########## 2. App Setup
#############################################
##### 1. Flask App #####
# General
entry_point = '/notebook-generator-website'
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

@app.route(entry_point)
def index():
	return render_template('index.html')

#############################################
########## 2. Analyze
#############################################

@app.route(entry_point+'/analyze')
def analyze():
	return render_template('analyze.html')

#############################################
########## 3. Search Data
#############################################

@app.route(entry_point+'/analyze/search')
def search_data():
	d = pd.read_sql_table('series', engine).head()
	return render_template('search_data.html', d=d)

#############################################
########## 4. Upload Data
#############################################

@app.route(entry_point+'/analyze/upload')
def upload_data():
	return render_template('upload_data.html')

#############################################
########## 5. Add Tools
#############################################

@app.route(entry_point+'/analyze/tools', methods=['GET', 'POST'])
def add_tools():
	f = request.form
	t = pd.read_sql_table('tool', engine).head()
	return render_template('add_tools.html', f=f, t=t)

#############################################
########## 6. Configure Analysis
#############################################

@app.route(entry_point+'/analyze/configure', methods=['GET', 'POST'])
def configure_analysis():
	f=request.form
	requires_signature = False if f.get('requires_signature') else True
	if requires_signature:
		s = pd.read_sql_query('SELECT gsm, sample_title FROM sample s LEFT JOIN series g ON g.id=s.series_fk WHERE gse = "{}"'.format(f.get('gse')), engine)
		return render_template('configure_signature.html', f=f, s=s)
	else:
		return render_template('review_analysis.html', f=f)

#############################################
########## 7. Generate Notebook
#############################################

@app.route(entry_point+'/analyze/generate', methods=['GET', 'POST'])
def generate_notebook():
	d = {key:value for key, value in request.form.lists()}
	return json.dumps(d)

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