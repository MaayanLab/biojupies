FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev
RUN apt-get update && apt-get install -y libmysqlclient-dev
RUN apt-get update && apt-get install -y virtualenv
RUN apt-get update && apt-get install --allow-unauthenticated -y r-base
RUN apt-get update && apt-get install -y wget
RUN apt-get update && apt-get install -y python3-setuptools
RUN apt-get update && apt-get install -y nginx uwsgi-core

RUN mkdir /notebook-generator-server; cd /notebook-generator-server; virtualenv -p /usr/bin/python3 venv/; 

RUN . /notebook-generator-server/venv/bin/activate && pip3 install numpy
RUN . /notebook-generator-server/venv/bin/activate && pip3 install pandas
RUN . /notebook-generator-server/venv/bin/activate && pip3 install Flask
RUN . /notebook-generator-server/venv/bin/activate && pip3 install sqlalchemy
RUN . /notebook-generator-server/venv/bin/activate && pip3 install flask-sqlalchemy
RUN . /notebook-generator-server/venv/bin/activate && pip3 install pymysql
RUN . /notebook-generator-server/venv/bin/activate && pip3 install nbformat
RUN . /notebook-generator-server/venv/bin/activate && pip3 install nbconvert
RUN . /notebook-generator-server/venv/bin/activate && pip3 install google-cloud
RUN . /notebook-generator-server/venv/bin/activate && pip3 install jupyter
RUN . /notebook-generator-server/venv/bin/activate && pip3 install jupyter_client
RUN . /notebook-generator-server/venv/bin/activate && pip3 install seaborn
RUN . /notebook-generator-server/venv/bin/activate && pip3 install plotly
RUN . /notebook-generator-server/venv/bin/activate && pip3 install rpy2
RUN . /notebook-generator-server/venv/bin/activate && pip3 install h5py
RUN . /notebook-generator-server/venv/bin/activate && pip3 install sklearn
RUN . /notebook-generator-server/venv/bin/activate && pip3 install qgrid
RUN . /notebook-generator-server/venv/bin/activate && pip3 install clustergrammer-widget
RUN . /notebook-generator-server/venv/bin/activate && pip3 install matplotlib-venn
RUN . /notebook-generator-server/venv/bin/activate && pip3 install uwsgi

RUN echo "r <- getOption('repos'); r['CRAN'] <- 'http://cran.us.r-project.org'; options(repos = r);" > ~/.Rprofile
RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("limma");'
RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("edgeR");'

RUN apt-get update && apt-get install -y uwsgi-plugin-python3
RUN . /notebook-generator-server/venv/bin/activate && python3 -m ipykernel install --user --name venv --display-name "python3-venv"
RUN . /notebook-generator-server/venv/bin/activate && pip3 install tzlocal

RUN chmod -R 777 /root;
COPY . /notebook-generator-server
WORKDIR /notebook-generator-server
RUN chmod +x boot.sh; chmod -R 777 .;

RUN mkdir /download; chmod 777 /download;

RUN cd app/static; wget https://github.com/MaayanLab/notebook-generator/raw/05abdfd6f07080484ade66b58422e770615ca4ba/library.zip; rm -r library; unzip library.zip; cd /notebook-generator-server;

ENTRYPOINT mkdir -p .config/gcloud; echo $APPLICATION_DEFAULT_CREDENTIALS > $GOOGLE_APPLICATION_CREDENTIALS; ./boot.sh