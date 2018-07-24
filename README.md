# BioJupies
Automated generation of Jupyter Notebooks for RNA-seq data analysis via user interface.

### Table of Contents
1. [What is BioJupies?](#what-is-biojupies)
2. [How can I generate a notebook using BioJupies?](#how-can-i-generate-a-notebook-using-biojupies)
3. [How can I upload my RNA-seq data to BioJupies?](#how-can-i-upload-my-rna-seq-data-to-biojupies)
4. [What analyses can BioJupies perform?](#what-analyses-can-biojupies-perform)

##-What is BioJupies?
BioJupies is a web server which allows users to automatically generate Jupyter Notebooks from RNA-seq datasets through an intuitive interface, with no knowledge of coding required. The BioJupies can be accessed for free from http://biojupies.cloud.
![Screenshot of the BioJupies website landing page.](img/website.png)

## How can I generate a notebook using BioJupies?

Generating a notebook using BioJupies requires three steps:

![Screenshot of the BioJupies website landing page.](img/workflow.png)

1. First, **select an RNA-seq dataset** you with to analyze. You can upload FASTQ files, gene expression tables, or use a search engine to browse over 6,000 public datasets published in the [Gene Expression Omnibus](https://www.ncbi.nlm.nih.gov/geo/) and processed by [ARCHS4](https://amp.pharm.mssm.edu/archs4/).
2. Second, **add one or more computational tools** to analyze the data. BioJupies currently supports 14 plugins to perform exploratory data analysis, differential gene expression, enrichment analysis, and small molecule queries.
3. Third, **generate the notebook** with the desired settings. The notebook will be served to you through a URL, and can be easily downloaded and rerun on your local computer.

## How can I upload my RNA-seq data to BioJupies?
Users can upload their RNA-seq datasets for analysis at https://amp.pharm.mssm.edu/biojupies/upload. BioJupies currently supports uploading **RNA-seq datasets in the FASTQ format** or **tables of gene-level counts**.

![Screenshot of the BioJupies upload page.](img/upload.png)

**Note**: While the user may successfully generate a notebook from normalized gene expression counts or microarray data tables, we do not recommend doing so since the tools are **NOT** yet optimized to handle such data. Such results should be interpreted with caution.

The Enrichment Analysis and Small Molecule Query plugins currently support datasets uploaded with **gene symbols** as row identifiers. When uploading datasets with different identifiers (e.g. ENSEMBL IDs, Entrez IDs), please note that these plugins may not work properly. 

## What analyses can BioJupies perform?
BioJupies currently provides **14 RNA-seq data analysis plugins**, divided into four categories: Exploratory Data Analysis, Differential Gene Expression, Enrichment Analysis, and Small Molecule Queries.

For more information about the analysis plugins, visit https://github.com/MaayanLab/biojupies-plugins.

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## References
[BioJupies: Automated Generation of Interactive Notebooks for RNA-seq Data Analysis in the Cloud](https://doi.org/10.1101/352476) Torre, D., Lachmann, A., and Ma’ayan, A. (2018)

## License
This project is licensed under the Apache-2.0 License - see the [LICENSE.md](LICENSE.md) file for details


# BioJupies
---

Jupyter Notebooks provide an advent mean for making bioinformatics data analyses more transparent, accessible and reusable. However, creating notebooks requires a degree of programming expertise which is often prohibitive for common users. BioJupies is a Jupyter Notebook generator that enables users to easily create, store, and deploy Jupyter Notebooks containing RNA-seq data analyses. Through an intuitive interface, novice users can rapidly generate tailored reports to analyze their own RNA-seq data, or fetch data from over 4000 published studies currently available on the NCBI Gene Expression Omnibus (GEO). Users can additionally upload their own data for analysis, either as raw sequencing files or gene expression matrices with counts. The reports contain interactive data visualizations of the samples, differential expression and enrichment analyses, and queries of signatures against the LINCS L1000 dataset for small molecule that can either mimic or reverse the signatures. Generated notebooks are permanently stored on the cloud, made available through a public URL, and can be cited through a unique Digital Object Identifier (DOI). By combining an intuitive user interface for Jupyter Notebook generation, with options to upload customized analysis scripts, BioJupies Generator addresses computational needs of both experimental and computational biologists. The BioJupies web interface is available at: http://biojupies.cloud, and the BioJupies Chrome extension is available at: https://chrome.google.com/webstore/detail/biojupies-generator/picalhhlpcjhonibabfigihelpmpadel.
