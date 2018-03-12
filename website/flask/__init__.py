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
import sys, os, json, requests
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
	options = [
		{'link': 'search_data', 'icon': 'search', 'title': 'Search', 'description': 'Search thousands of ready-to-analyze datasets'},
		{'link': 'upload_data', 'icon': 'upload', 'title': 'Upload', 'description': 'Upload your own gene expression table or<br>RNA-seq reads'},
		{'link': 'index', 'icon': 'table', 'title': 'Example', 'description': 'Learn to generate notebooks with a<br>step-by-step tutorial'}
	]
	return render_template('analyze.html', options=options)

#############################################
########## 3. Search Data
#############################################

@app.route(entry_point+'/analyze/search')
def search_data():
	q = request.args.get('q', 'cancer')
	min_samples = request.args.get('min_samples', 5)
	max_samples = request.args.get('max_samples', 30)
	max_samples_q = 500 if max_samples == '70' else max_samples
	sortby = request.args.get('sortby', 'desc')
	d = pd.read_sql_query('SELECT gse, gpl, title, summary, COUNT(*) AS nr_samples FROM series se LEFT JOIN sample sa ON se.id=sa.series_fk LEFT JOIN platform p ON p.id=sa.platform_fk WHERE title LIKE "%%{q}%%" OR summary LIKE "%%{q}%%" GROUP BY gse HAVING nr_samples >= {min_samples} AND nr_samples <= {max_samples_q} ORDER BY nr_samples {sortby}'.format(**locals()), engine).head(20).to_dict(orient='records')
	return render_template('search_data.html', d=d, min_samples=min_samples, max_samples=max_samples)

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
	t = pd.read_sql_table('tool', engine).to_dict(orient='records')
	d = {'gse': request.form.get('gse-gpl').split('-')[0], 'gpl': request.form.get('gse-gpl').split('-')[1]}
	return render_template('add_tools.html', d=d, t=t)

#############################################
########## 6. Configure Analysis
#############################################

@app.route(entry_point+'/analyze/configure', methods=['GET', 'POST'])
def configure_analysis():
	f=request.form
	signature_tools = pd.read_sql_query('SELECT tool_string FROM tool WHERE requires_signature = TRUE', engine)['tool_string'].values
	requires_signature = any([x in signature_tools for x in [x for x in f.lists()][-1][-1]])
	if requires_signature:
		j = pd.read_sql_query('SELECT DISTINCT CONCAT(gsm, "---", sample_title) AS sample_info, variable, value FROM sample s LEFT JOIN series g ON g.id=s.series_fk LEFT JOIN sample_metadata sm ON s.id=sm.sample_fk WHERE gse = "{}"'.format(f.get('gse')), engine).pivot(index='sample_info', columns='variable', values='value')
		j = pd.concat([pd.DataFrame({'accession': [x.split('---')[0] for x in j.index], 'sample': [x.split('---')[1] for x in j.index]}, index=j.index), j], axis=1).reset_index(drop=True).fillna('')
		j = j[[col for col, colData in j.iteritems() if len(colData.unique()) > 1]]
		return render_template('configure_signature.html', f=f, j=j)
	else:
		tools = [value for value, key in zip(f.listvalues(), f.keys()) if key == 'tool'][0]
		tool_query_string = '("'+'","'.join([value for value, key in zip(f.listvalues(), f.keys()) if key == 'tool'][0])+'")'
		p = pd.read_sql_query('SELECT tool_name, tool_string, tool_description, parameter_name, parameter_description, parameter_string, value, `default` FROM tool t LEFT JOIN parameter p ON t.id=p.tool_fk LEFT JOIN parameter_value pv ON p.id=pv.parameter_fk WHERE t.tool_string IN {}'.format(tool_query_string), engine).set_index(['tool_string'])#.set_index(['tool_name', 'parameter_name', 'parameter_description', 'parameter_string'])
		t = p[['tool_name', 'tool_description']].drop_duplicates().reset_index().set_index('tool_string', drop=False).to_dict(orient='index')#.groupby('tool_string')[['tool_name', 'tool_description']]#.apply(tuple).to_frame()#drop_duplicates().to_dict(orient='index')
		p_dict = {tool_string: p.drop(['tool_description', 'tool_name', 'value', 'default'], axis=1).loc[tool_string].drop_duplicates().to_dict(orient='records') if not isinstance(p.loc[tool_string], pd.Series) else [] for tool_string in tools}
		for tool_string, parameters in p_dict.items():
			for parameter in parameters:
				parameter['values'] = p.reset_index().set_index(['tool_string', 'parameter_string'])[['value', 'default']].dropna().loc[(tool_string, parameter['parameter_string'])].to_dict(orient='records')
		for tool_string in t.keys():
			t[tool_string]['parameters'] = p_dict[tool_string]
		t = [t[x] for x in tools]
		return render_template('review_analysis.html', t=t, f=f)

#############################################
########## 7. Generate Notebook
#############################################

@app.route(entry_point+'/analyze/generate', methods=['GET', 'POST'])
def generate_notebook():
	d = {key:value if len(value) > 1 else value[0] for key, value in request.form.lists()}
	p = {x:{} for x in d['tool']}
	g = {x:[] for x in ['a', 'b', 'none']}
	print(d)
	for key, value in d.items():
		if '-' in key:
			if 'GSM' in key:
				g[value[0]].append(key.split('-')[0])
			else:
				tool_string, parameter_string = key.split('-')
				p[tool_string][parameter_string] = value

	c = {
		'notebook': {'title': d.get('notebook_title'), 'live': 'False', 'version': 'v0.3'},
		'tools': [{'tool_string': x, 'parameters': p.get(x, {})} for x in d['tool']],
		'data': {'source': 'archs4', 'parameters': {'gse': d['gse'], 'platform': d['gpl']}},
		'signature': {"method": "limma",
			"A": {"name": d.get('group_a_label'), "samples": g['a']},
			"B": {"name": d.get('group_b_label'), "samples": g['b']}}
	}
	r = requests.post('http://amp.pharm.mssm.edu/notebook-generator-server/api/generate', data=json.dumps(c), headers={'content-type':'application/json'})
	return r.text

#############################################
########## 9. Search Datasets
#############################################

@app.route(entry_point+'/api/search_datasets', methods=['POST'])
def search_datasets():
	d = pd.read_sql_query('SELECT gse, gpl, title, summary, COUNT(*) AS nr_samples FROM series se LEFT JOIN sample sa ON se.id=sa.series_fk LEFT JOIN platform p ON p.id=sa.platform_fk WHERE title LIKE "%%{search}%%" OR summary LIKE "%%{search}%%" GROUP BY gse LIMIT 50'.format(**request.json), engine)
	return json.dumps(d.to_dict(orient='records'))

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