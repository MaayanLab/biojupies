# BioJupies
Automated generation of Jupyter Notebooks for RNA-seq data analysis via user interface.

## What is BioJupies?
BioJupies is a website which allows users to automatically generate Jupyter Notebooks from raw RNA-seq data through an intuitive interface, with no knowledge of coding required. The BioJupies website can be accessed for free at http://biojupies.cloud.
![Screenshot of the BioJupies website landing page.](img/website.png)

### Prerequisites

What things you need to install the software and how to install them

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

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc


# BioJupies
---

Jupyter Notebooks provide an advent mean for making bioinformatics data analyses more transparent, accessible and reusable. However, creating notebooks requires a degree of programming expertise which is often prohibitive for common users. BioJupies is a Jupyter Notebook generator that enables users to easily create, store, and deploy Jupyter Notebooks containing RNA-seq data analyses. Through an intuitive interface, novice users can rapidly generate tailored reports to analyze their own RNA-seq data, or fetch data from over 4000 published studies currently available on the NCBI Gene Expression Omnibus (GEO). Users can additionally upload their own data for analysis, either as raw sequencing files or gene expression matrices with counts. The reports contain interactive data visualizations of the samples, differential expression and enrichment analyses, and queries of signatures against the LINCS L1000 dataset for small molecule that can either mimic or reverse the signatures. Generated notebooks are permanently stored on the cloud, made available through a public URL, and can be cited through a unique Digital Object Identifier (DOI). By combining an intuitive user interface for Jupyter Notebook generation, with options to upload customized analysis scripts, BioJupies Generator addresses computational needs of both experimental and computational biologists. The BioJupies web interface is available at: http://biojupies.cloud, and the BioJupies Chrome extension is available at: https://chrome.google.com/webstore/detail/biojupies-generator/picalhhlpcjhonibabfigihelpmpadel.
