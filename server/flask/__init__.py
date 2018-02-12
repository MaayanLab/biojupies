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
	# gse_list = json.loads(request.get_data())['gse']
	gse_list = ["GSE108500","GSE94902","GSE94928","GSE95021","GSE95020","GSE94980","GSE94979","GSE102855","GSE102852","GSE103938","GSE110383","GSE110387","GSE110386","GSE107313","GSE110220","GSE104968","GSE104967","GSE104966","GSE104964","GSE69770","GSE97831","GSE103550","GSE103548","GSE102744","GSE107556","GSE107555","GSE102294","GSE108693","GSE79789","GSE110180","GSE110114","GSE95027","GSE94574","GSE94570","GSE110149","GSE101539","GSE109387","GSE104730","GSE104559","GSE108601","GSE65523","GSE86458","GSE107047","GSE101287","GSE94874","GSE106626","GSE108615","GSE108614","GSE105088","GSE99022","GSE101745","GSE105447","GSE109485","GSE109542","GSE69157","GSE97225","GSE97223","GSE102155","GSE109955","GSE94332","GSE103420","GSE109287","GSE109903","GSE103520","GSE103531","GSE87686","GSE87685","GSE87624","GSE82183","GSE109821","GSE109798","GSE109793","GSE107194","GSE108354","GSE108353","GSE80153","GSE80154","GSE84659","GSE99133","GSE108699","GSE107530","GSE109694","GSE109653","GSE78497","GSE99088","GSE107195","GSE106989","GSE103021","GSE107307","GSE103790","GSE109528","GSE109522","GSE109490","GSE109483","GSE102616","GSE93628","GSE93627","GSE95656","GSE95130","GSE95132","GSE106261","GSE91061","GSE100990","GSE105083","GSE108753","GSE93911","GSE106901","GSE107542","GSE101665","GSE109463","GSE109418","GSE108763","GSE102721","GSE109373","GSE95013","GSE109279","GSE102937","GSE107915","GSE102727","GSE103471","GSE107801","GSE93709","GSE100684","GSE106423","GSE99233","GSE74230","GSE95542","GSE97450","GSE98183","GSE104552","GSE100076","GSE100075","GSE90830","GSE97037","GSE101480","GSE109072","GSE99149","GSE103876","GSE103350","GSE86855","GSE109028","GSE96634","GSE108308","GSE108883","GSE107096","GSE107670","GSE99808","GSE104309","GSE104308","GSE108811","GSE93309","GSE108757","GSE107196","GSE103907","GSE93069","GSE95478","GSE108495","GSE97993","GSE106107","GSE97389","GSE80776","GSE100092","GSE90153","GSE106844","GSE104264","GSE104633","GSE94373","GSE94375","GSE94369","GSE93904","GSE103934","GSE99867","GSE84820","GSE90519","GSE107053","GSE107117","GSE103602","GSE67934","GSE86280","GSE80777","GSE98091","GSE80358","GSE79988","GSE98871","GSE88830","GSE75743","GSE75742","GSE75741","GSE80619","GSE102305","GSE100465","GSE100464","GSE107762","GSE99626","GSE81925","GSE82142","GSE97443","GSE97408","GSE92943","GSE108528","GSE106330","GSE102753","GSE94243","GSE108391","GSE107518","GSE72403","GSE101297","GSE104054","GSE89799","GSE88741","GSE107470","GSE107590","GSE98760","GSE108367","GSE108334","GSE86065","GSE108322","GSE78957","GSE100530","GSE94528","GSE94999","GSE95011","GSE85731","GSE100276","GSE100385","GSE108140","GSE96035","GSE106291","GSE102762","GSE107395","GSE95294","GSE95293","GSE107289","GSE107281","GSE81084","GSE108111","GSE108041","GSE87187","GSE87189","GSE91062","GSE108013","GSE95541","GSE95537","GSE98496","GSE106273","GSE103895","GSE103850","GSE108004","GSE108003","GSE98050","GSE101997","GSE101995","GSE101994","GSE87514","GSE87511","GSE92344","GSE101972","GSE107848","GSE64082","GSE92322","GSE107030","GSE104294","GSE107783","GSE107735","GSE104855","GSE106605","GSE95374","GSE67807","GSE107653","GSE67863","GSE105138","GSE105137","GSE105166","GSE100797","GSE107601","GSE85432","GSE85431","GSE107581","GSE106760","GSE106804","GSE106336","GSE99820","GSE99857","GSE94355","GSE85003","GSE85001","GSE107560","GSE107559","GSE103243","GSE103242","GSE104188","GSE95751","GSE95750","GSE53190","GSE79989","GSE84852","GSE92316","GSE107035","GSE103001","GSE98831","GSE103322","GSE107502","GSE101708","GSE104592","GSE94613","GSE94583","GSE79278","GSE89569","GSE87326","GSE83763","GSE107389","GSE101638","GSE107245","GSE91056","GSE91052","GSE101209","GSE89477","GSE90885","GSE90503","GSE84914","GSE90459","GSE92489","GSE76032","GSE75943","GSE89952","GSE78795","GSE96860","GSE96867","GSE107220","GSE83865","GSE92842","GSE103868","GSE104766","GSE107182","GSE107181","GSE107180","GSE103663","GSE103662","GSE106681","GSE106695","GSE106694","GSE97947","GSE63356","GSE75677","GSE104736","GSE87585","GSE99101","GSE94488","GSE99521","GSE100607","GSE99923","GSE86387","GSE104658","GSE104657","GSE84389","GSE83788","GSE83786","GSE93566","GSE93533","GSE102652","GSE106886","GSE93722","GSE102511","GSE106839","GSE84073","GSE98122","GSE63230","GSE104118","GSE106391","GSE89745","GSE99304","GSE86026","GSE86024","GSE93308","GSE93306","GSE106696","GSE106674","GSE99906","GSE101526","GSE99641","GSE87681","GSE89672","GSE106545","GSE98644","GSE99671","GSE89478","GSE102467","GSE87563","GSE105043","GSE81407","GSE74762","GSE84465","GSE105159","GSE85559","GSE102910","GSE105035","GSE104513","GSE103152","GSE106387","GSE98898","GSE92744","GSE89419","GSE79463","GSE104519","GSE94082","GSE81941","GSE70810","GSE69599","GSE90781","GSE92260","GSE106304","GSE106303","GSE95048","GSE95277","GSE95169","GSE95168","GSE77231","GSE94566","GSE74345","GSE101923","GSE103567","GSE106092","GSE101772","GSE103240","GSE95782","GSE101419","GSE104517","GSE104507","GSE89129","GSE89127","GSE71876","GSE98469","GSE94503","GSE94502","GSE69507","GSE69506","GSE105142","GSE97137","GSE74176","GSE103559","GSE101767","GSE102060","GSE99209","GSE91377","GSE102246","GSE99479","GSE87541","GSE98860","GSE103525","GSE103524","GSE103538","GSE104876","GSE104873","GSE104854","GSE84275","GSE93417","GSE93416","GSE102597","GSE104836","GSE104777","GSE81222","GSE99794","GSE96056","GSE99381","GSE95413","GSE104209","GSE104714","GSE85089","GSE104334","GSE88978","GSE88977","GSE93644","GSE101927","GSE103252","GSE102443","GSE104463","GSE86237","GSE72577","GSE79082","GSE88841","GSE86460","GSE87535","GSE103366","GSE95513","GSE86792","GSE102170","GSE89992","GSE77894","GSE77893","GSE77892","GSE77891","GSE74138","GSE90652","GSE90673","GSE103646","GSE104138","GSE98592","GSE104443","GSE104380","GSE99466"]
	
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