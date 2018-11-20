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
RUN apt-get update && apt-get install -y uwsgi-plugin-python3

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
RUN . /notebook-generator-server/venv/bin/activate && pip3 install tzlocal

RUN . /notebook-generator-server/venv/bin/activate && python -m ipykernel install --user --name venv --display-name "python3-venv"

RUN echo "r <- getOption('repos'); r['CRAN'] <- 'http://cran.us.r-project.org'; options(repos = r);" > ~/.Rprofile
RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("limma");'
RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("edgeR");'
RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("preprocessCore");'

RUN . /notebook-generator-server/venv/bin/activate && pip3 install flask-cors
RUN . /notebook-generator-server/venv/bin/activate && pip3 install flask-mail
RUN . /notebook-generator-server/venv/bin/activate && pip3 install sentry-sdk[flask]==0.3.5

ENV LIBRARY_VERSION=v1.0.2

COPY . /notebook-generator-server  
WORKDIR /notebook-generator-server
RUN chmod +x boot.sh download_library.sh; ./download_library.sh

ENTRYPOINT mkdir -p .config/gcloud; echo $APPLICATION_DEFAULT_CREDENTIALS > $GOOGLE_APPLICATION_CREDENTIALS; ./boot.sh