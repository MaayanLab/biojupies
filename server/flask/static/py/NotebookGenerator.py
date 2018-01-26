#################################################################
#################################################################
############### Notebook Generator API ##########################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#################################################################
#################################################################
############### 1. Library Configuration ########################
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. Python modules #####
import nbformat as nbf
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config

#############################################
########## 2. Variables
#############################################
##### 1. Helper Function #####
def addCell(notebook, content, celltype='code'):
	if celltype == 'code':
		notebook['cells'].append(nbf.v4.new_code_cell(content))
	elif celltype == 'markdown':
		notebook['cells'].append(nbf.v4.new_markdown_cell(content))

##### 2. Notebook Execution #####
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

##### 3. Notebook Conversion #####
c = Config()
c.HTMLExporter.preprocessors = ['nbconvert.preprocessors.ExtractOutputPreprocessor']
html_exporter_with_figs = HTMLExporter(config=c)

#############################################
########## 3. Text
#############################################



#################################################################
#################################################################
############### 1. Tools ########################################
#################################################################
#################################################################

#############################################
########## 1. Fetch data
#############################################

def fetch_dataset(notebook, dataset_accession, platform):
	# Introduction
	intro_string = '''
<h2 style="margin-top: 0px;" id="fetch_dataset">2.1 Data Download</h2>
<p>The dataset is extracted from ARCHS4 and loaded in the Jupyter environment.</p>
	'''.format(**locals())
	notebook['cells'].append(nbf.v4.new_markdown_cell(intro_string))

	# Code
	if platform:
		notebook['cells'].append(nbf.v4.new_code_cell('# Fetch data \ndata = fetch_dataset("{dataset_accession}", platform="{platform}") \ndata["readcounts"].head()'.format(**locals())))
	else:
		notebook['cells'].append(nbf.v4.new_code_cell('# Fetch data \ndata = fetch_dataset("{dataset_accession}") \ndata["readcounts"].head()'.format(**locals())))


	# Read counts
	notebook['cells'].append(nbf.v4.new_markdown_cell('<b>Table 1 | Raw readcount dataframe from ARCHS4.</b> Whatever.'.format(**locals())))

	# Sample metadata
	notebook['cells'].append(nbf.v4.new_code_cell('data["sample_metadata"]'))
	notebook['cells'].append(nbf.v4.new_markdown_cell('<b>Table 2 | Asd.</b> Whatever.'.format(**locals())))

	return notebook

#############################################
########## 2. Library sizes
#############################################

def library_sizes(notebook, number):
	# Introduction
	intro_string = '''
<h2 style="margin-top: 0px;" id="library_sizes">2.{number} Plot Library Sizes</h2>
<p>Here we analyze stuff.</p>
	'''.format(**locals())
	notebook['cells'].append(nbf.v4.new_markdown_cell(intro_string))

	# Code
	notebook['cells'].append(nbf.v4.new_code_cell('# Plot Library Sizes \nresults["library_sizes"] = analyze(rawcount_dataframe = data["readcounts"], tool_name = "library_sizes") \nplot(results["library_sizes"])'))

	# Legend
	notebook['cells'].append(nbf.v4.new_markdown_cell('<b>Figure 2.{number} | Asd.</b> Whatever.'.format(**locals())))
	return notebook

#############################################
########## 3. Clustermap
#############################################

def clustermap(notebook, number):
	# Introduction
	intro_string = '''
<h2 style="margin-top: 0px;" id="clustermap">2.{number} Clustermap</h2>
<p>Here we analyze stuff.</p>
	'''.format(**locals())
	notebook['cells'].append(nbf.v4.new_markdown_cell(intro_string))

	# Code
	notebook['cells'].append(nbf.v4.new_code_cell('# Plot Clustered Heatmap \nplot(data["readcounts"], tool_name="clustermap")'))

	# Legend
	notebook['cells'].append(nbf.v4.new_markdown_cell('<b>Figure 2.{number} | Asd.</b> Whatever.'.format(**locals())))
	return notebook

#############################################
########## 4. PCA
#############################################

def pca(notebook, number):
	# Introduction
	intro_string = '''
<h2 style="margin-top: 0px;" id="pca">2.{number} Principal Components Analysis</h2>
<p>Here we analyze stuff.</p>
	'''.format(**locals())
	notebook['cells'].append(nbf.v4.new_markdown_cell(intro_string))

	# Code
	notebook['cells'].append(nbf.v4.new_code_cell('# Plot PCA \nresults["pca"] = analyze(expression_dataframe = data["readcounts"], tool_name = "pca")\nplot(results["pca"])'))

	# Legend
	notebook['cells'].append(nbf.v4.new_markdown_cell('<b>Figure 2.{number} | Asd.</b> Whatever.'.format(**locals())))
	return notebook

#############################################
########## 5. Limma
#############################################

def limma(notebook, control_samples, experimental_samples, signature_name, number):
	# Introduction
	intro_string = '''
<h2 style="margin-top: 0px;" id="pca">2.{number} Signature Analysis</h2>
<p>Here we analyze signature {signature_name}:</p>
<ul>
<li><b>Control samples:</b> {control_samples}</li>
<li><b>Experimental samples:</b> {experimental_samples}</li>
</ul>
	'''.format(**locals())
	notebook['cells'].append(nbf.v4.new_markdown_cell(intro_string))

	# Code
	notebook['cells'].append(nbf.v4.new_code_cell('# Compute Signature \nsignature = analyze(rawcount_dataframe = data["readcounts"],\n\ttool_name = "limma",\n\tcontrol_samples={control_samples},\n\texperimental_samples={experimental_samples},\n\tsignature_name="{signature_name}")'.format(**locals())))
	notebook['cells'].append(nbf.v4.new_code_cell('# MA Plot \nplot(signature, plot_type="ma")'))
	notebook['cells'].append(nbf.v4.new_code_cell('# Volcano Plot \nplot(signature, plot_type="volcano")'))

	# Legend
	notebook['cells'].append(nbf.v4.new_markdown_cell('<b>Figure 2.{number} | Asd.</b> Whatever.'.format(**locals())))
	return notebook

#############################################
########## 6. Enrichr
#############################################

def enrichr(notebook, number):
	# Introduction
	intro_string = '''
<h2 style="margin-top: 0px;" id="pca">2.{number} Enrichment Analysis</h2>
<p>Here we analyze signature:</p>
	'''.format(**locals())
	notebook['cells'].append(nbf.v4.new_markdown_cell(intro_string))

	# Code
	notebook['cells'].append(nbf.v4.new_code_cell('# Run Enrichr \nresults["enrichr"] = analyze(signature = signature, tool_name = "enrichr") \nplot(results["enrichr"])'.format(**locals())))

	# Legend
	notebook['cells'].append(nbf.v4.new_markdown_cell('<b>Figure 2.{number} | Asd.</b> Whatever.'.format(**locals())))
	return notebook

#################################################################
#################################################################
############### 2. Toolkits #####################################
#################################################################
#################################################################

#############################################
########## 1. Exploratory Data Analysis
#############################################

def eda(notebook, config):

	# Intro
	intro_string = '''
<div style="font-size:27pt;font-weight:500;margin-top:10px;margin-bottom:40px;"> {dataset_accession} | Exploratory Data Analysis</div>
<h1>1. Overview</h1>
<p>This notebook contains a basic exploratory data analysis of GEO dataset {dataset_accession}.</p>
<h2>1.1 Sections</h2>
<p>The notebook is divided in the following sections:</p>
<ol>
	<li><a href="#fetch_dataset"><b>Data Download</b></a>.</li>
	<li><a href="#library_sizes"><b>Library Size Analysis</b></a>.</li>
	<li><a href="#clustermap"><b>Clustered Heatmap Analysis</b></a>.</li>
	<li><a href="#pca"><b>Principal Components Analysis</b></a>.</li>
</ol>
<h1>2. Analysis</h1>
	'''.format(**config)
	notebook['cells'].append(nbf.v4.new_markdown_cell(intro_string))

	# 1. Fetch Dataset
	notebook = fetch_dataset(notebook, dataset_accession = config['dataset_accession'], platform = config.get('platform'))

	# 2. Library Sizes
	notebook = library_sizes(notebook, number=2)

	# 3. Clustermap
	notebook = clustermap(notebook, number=3)

	# 4. PCA
	notebook = pca(notebook, number=4)

	return notebook

#############################################
########## 2. Signature Analysis
#############################################

def signature_analysis(notebook, config):

	# Intro
	intro_string = '''
<div style="font-size:27pt;font-weight:500;margin-top:10px;margin-bottom:40px;"> {dataset_accession} | Signature Analysis</div>
<h1>1. Overview</h1>
<p>This notebook contains an analysis of signatures for GEO dataset {dataset_accession}.</p>
<h2>1.1 Sections</h2>
<p>The notebook is divided in the following sections:</p>
<ol>
	<li><a href="#fetch_dataset"><b>Data Download</b></a>.</li>
	<li><a href="#add_signature"><b>Signature Definition</b></a>.</li>
</ol>
<h1>2. Analysis</h1>
	'''.format(**config)
	notebook['cells'].append(nbf.v4.new_markdown_cell(intro_string))

	# 1. Fetch Dataset
	notebook = fetch_dataset(notebook, dataset_accession = config['dataset_accession'], platform = config.get('platform'))

	# 2. Get Signature
	notebook = limma(notebook, control_samples=config['control_samples'].split(','), experimental_samples=config['experimental_samples'].split(','), signature_name=config['signature_name'], number=2)

	# 3. Run Enrichment Analysis
	notebook = enrichr(notebook, number=3)

	return notebook

#################################################################
#################################################################
############### 3. Wrapper ######################################
#################################################################
#################################################################

#############################################
########## 1. Generate Notebook
#############################################

def GenerateNotebook(config):

	# Initialize Notebook
	notebook = nbf.v4.new_notebook()

	# Add init cells
	notebook['cells'].append(nbf.v4.new_code_cell('# Initialize Environment\n%run static/lib/v1.0/init.ipy'))
	notebook['cells'].append(nbf.v4.new_code_cell("""HTML('''<script> code_show=true;  function code_toggle() {  if (code_show){  $('div.input').hide();  } else {  $('div.input').show();  }  code_show = !code_show }  $( document ).ready(code_toggle); </script> <form action="javascript:code_toggle()"><input type="submit" value="Toggle Code"></form>''')"""))

	# Get Notebook
	notebook = eval('{toolkit}(notebook = notebook, config = config)'.format(**config))

	# Execute
	# ep.preprocess(notebook, {'metadata': {'path': '.'}})

	# Convert
	# notebook_html = html_exporter_with_figs.from_notebook_node(notebook)[0]
	notebook_html = nbf.writes(notebook)

	# Return
	return notebook_html

