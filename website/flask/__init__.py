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
import sys, os, json, requests, re
import pandas as pd
import pymysql
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
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
engine = db.engine

# Notebook Generation
version = 'v0.3'

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
	return render_template('analyze/analyze.html', options=options)

#############################################
########## 3. Search Data
#############################################

@app.route(entry_point+'/analyze/search')
def search_data():
	# Search Datasets
	q = request.args.get('q', 'cancer')
	min_samples = request.args.get('min_samples', 5)
	max_samples = request.args.get('max_samples', 30)
	max_samples_q = 500 if max_samples == '70' else max_samples
	sortby = request.args.get('sortby', '')
	sortby = 'ORDER BY nr_samples {}, date DESC'.format(sortby) if sortby in ['desc', 'asc'] else 'ORDER BY `date` DESC'
	organism = request.args.get('organism', 'all')
	organism_q = '", "'.join([x for x in ['Human', 'Mouse'] if organism == 'all' or x == organism.title()])
	d = pd.read_sql_query('SELECT gse, gpl, organism, title, summary, `date`, COUNT(*) AS nr_samples FROM series se LEFT JOIN sample sa ON se.id=sa.series_fk LEFT JOIN platform p ON p.id=sa.platform_fk WHERE title LIKE "%% {q} %%" OR summary LIKE "%% {q} %%" OR gse LIKE "{q}%%" GROUP BY gse HAVING organism IN ("{organism_q}") AND nr_samples >= {min_samples} AND nr_samples <= {max_samples_q} {sortby}'.format(**locals()), engine).head(20)
	# Highlight searched term
	h = lambda x: '<span class="highlight">{}</span>'.format(x)
	for col in ['title', 'summary']:
		d[col] = [x.replace(q, h(q)).replace(q.title(), h(q.title())).replace(q.lower(), h(q.lower())).replace(q.upper(), h(q.upper())) for x in d[col]]
	d = d.to_dict(orient='records')
	return render_template('analyze/search_data.html', d=d, min_samples=min_samples, max_samples=max_samples, q=q)	

#############################################
########## 4. Add Tools
#############################################

@app.route(entry_point+'/analyze/tools', methods=['GET', 'POST'])
def add_tools():
	# Get dataset
	d = {'uid': request.args.get('uid'), 'source': 'upload'} if 'uid' in request.args.keys() else {'gse': request.form.get('gse-gpl').split('-')[0], 'gpl': request.form.get('gse-gpl').split('-')[1], 'source': 'archs4'}
	# Get tool data
	t = pd.read_sql_query('SELECT * FROM tool t LEFT JOIN section s ON s.id=t.section_fk', engine)
	t['tool_documentation'] = ['https://github.com/denis-torre/notebook-generator/tree/master/library/{version}/analysis_tools/'.format(**globals())+x for x in t['tool_string']]
	t_data = t.set_index('tool_string', drop=False).to_dict(orient='index')
	t['tool_data'] = [t_data[x] for x in t['tool_string']]
	s = t.groupby('section_name')['tool_data'].apply(tuple).reindex(['Dimensionality Reduction', 'Data Visualization', 'Differential Expression Analysis', 'Signature Analysis'])
	return render_template('analyze/add_tools.html', d=d, s=s)

#############################################
########## 5. Configure Analysis
#############################################

@app.route(entry_point+'/analyze/configure', methods=['GET', 'POST'])
def configure_analysis():
	# Get form
	f=request.form
	# Check if requires signature
	signature_tools = pd.read_sql_query('SELECT tool_string FROM tool WHERE requires_signature = TRUE', engine)['tool_string'].values
	requires_signature = any([x in signature_tools for x in [x for x in f.lists()][-1][-1]])
	if requires_signature:
		# Get samples
		if 'gse' in request.form.keys():
			j = pd.read_sql_query('SELECT DISTINCT CONCAT(gsm, "---", sample_title) AS sample_info, variable, value FROM sample s LEFT JOIN series g ON g.id=s.series_fk LEFT JOIN sample_metadata sm ON s.id=sm.sample_fk WHERE gse = "{}"'.format(f.get('gse')), engine).pivot(index='sample_info', columns='variable', values='value')
			j = pd.concat([pd.DataFrame({'accession': [x.split('---')[0] for x in j.index], 'sample': [x.split('---')[1] for x in j.index]}, index=j.index), j], axis=1).reset_index(drop=True).fillna('')
			j = j[[col for col, colData in j.iteritems() if len(colData.unique()) > 1]]
		else:
			j = pd.read_sql_query('SELECT DISTINCT sample_name AS sample, variable, value FROM user_dataset ud LEFT JOIN user_sample us ON ud.id=us.user_dataset_fk LEFT JOIN user_sample_metadata usm ON us.id=usm.user_sample_fk WHERE ud.dataset_uid="{}"'.format(request.form.get('uid')), engine)
			j = j.pivot(index='sample', columns='variable', values='value').reset_index()
			print(j.head())
		return render_template('analyze/configure_signature.html', f=f, j=j)
	else:
		# Get tool parameters
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
		return render_template('analyze/review_analysis.html', t=t, f=f)

#############################################
########## 6. Generate Notebook
#############################################

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

	c = {
		'notebook': {'title': d.get('notebook_title'), 'live': 'False', 'version': version},
		'tools': [{'tool_string': x, 'parameters': p.get(x, {})} for x in d['tool']],
		'data': {'source': d['source'], 'parameters': {'gse': d['gse'], 'platform': d['gpl']} if 'gse' in d.keys() and 'gpl' in d.keys() else {'uid': d['uid']}},
		'signature': {"method": "limma",
			"A": {"name": d.get('group_a_label'), "samples": g['a']},
			"B": {"name": d.get('group_b_label'), "samples": g['b']}}
	}
	# r = requests.post('http://amp.pharm.mssm.edu/notebook-generator-server/api/generate', data=json.dumps(c), headers={'content-type':'application/json'})
	return render_template('analyze/results.html', notebook_configuration=json.dumps(c))

#############################################
########## 7. Upload Data
#############################################

@app.route(entry_point+'/upload')
def upload_data():
	options = [
		{'link': 'upload_table', 'icon': 'table', 'title': 'Expression Table', 'description': 'Text file containing numeric<br>gene expression values'},
		{'link': 'upload_reads', 'icon': 'dna', 'title': 'RNA-seq Reads', 'description': 'Read files generated from<br>an RNA-seq analysis'}
	]
	return render_template('upload/upload.html', options=options)

#############################################
########## 8. Upload Table
#############################################

@app.route(entry_point+'/upload/table', methods=['GET', 'POST'])
def upload_table():
	f = request.form
	if not len(f):
		return render_template('upload/upload_table.html')
	elif 'metadata' not in f.to_dict().keys():
		samples = json.loads(f.to_dict()['expression'])['columns']
		samples.sort()
		return render_template('upload/upload_metadata.html', samples=samples, f=f)
	else:
		# Process metadata dataframe
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
		return render_template('upload/upload_table_loading.html', f=f)

#############################################
########## 9. Upload Table API
#############################################

@app.route(entry_point+'/api/upload/expression', methods=['POST'])
def upload_expression_api():

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
	return dataframe_json

#############################################
########## 10. Upload Metadata API
#############################################

@app.route(entry_point+'/api/upload/metadata', methods=['POST'])
def upload_metadata_api():

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
	return dataframe_json

#############################################
########## 11. Upload Table API
#############################################

@app.route(entry_point+'/api/upload/table', methods=['POST'])
def upload_table_api():

	# Get ID
	results = TM.uploadTable(request.data, engine)

	return results

#############################################
########## 12. Upload Reads
#############################################

@app.route(entry_point+'/upload/reads')
def upload_reads():
	return render_template('upload/upload_reads.html')

#############################################
########## 13. Upload Reads API
#############################################

@app.route(entry_point+'/api/upload/reads', methods=['POST'])
def upload_reads_api():
	return ''

#############################################
########## 14. Upload Results
#############################################

@app.route(entry_point+'/upload/results', methods=['GET', 'POST'])
def upload_results():
	f = request.form
	return render_template('upload/upload_table_results.html', f=f)

#############################################
########## 15. Uploaded Data
#############################################

@app.route(entry_point+'/analyze/uploaded_datasets', methods=['GET', 'POST'])
def uploaded_datasets():
	return render_template('upload/uploaded_datasets.html')

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