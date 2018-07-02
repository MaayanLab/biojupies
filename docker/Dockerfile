FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev
RUN apt-get update && apt-get install -y libmysqlclient-dev

RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install Flask
RUN pip3 install sqlalchemy
RUN pip3 install flask-sqlalchemy
RUN pip3 install pymysql
RUN pip3 install nbformat
RUN pip3 install nbconvert
RUN pip3 install google-cloud
RUN pip3 install jupyter
RUN pip3 install jupyter_client

RUN pip3 install seaborn
RUN pip3 install plotly

RUN apt-get update && apt-get install --allow-unauthenticated -y r-base

RUN pip3 install rpy2
RUN pip3 install h5py
RUN pip3 install sklearn
RUN pip3 install qgrid
RUN pip3 install clustergrammer-widget

RUN echo "r <- getOption('repos'); r['CRAN'] <- 'http://cran.us.r-project.org'; options(repos = r);" > ~/.Rprofile
RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("limma");'
RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("edgeR");'

RUN apt-get update && apt-get install -y wget

RUN pip3 install matplotlib-venn

RUN mkdir /notebooks /library /download

COPY . /library
RUN cd /library; python3 download_libraries.py 
WORKDIR /notebooks

ENTRYPOINT python3 /library/launch.py; jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser --notebook-dir='/notebooks' --NotebookApp.iopub_data_rate_limit=10000000000 --NotebookApp.token=