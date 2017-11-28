FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev
RUN apt-get update && apt-get install -y r-base

RUN pip3 install --upgrade pip
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install jupyter
RUN pip3 install scipy
RUN pip3 install seaborn
RUN pip3 install sklearn
RUN pip3 install clustergrammer-widget
RUN pip3 install plotly
RUN pip3 install rpy2
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension
RUN jupyter nbextension enable --py --sys-prefix clustergrammer_widget

RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("limma");'
RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("edgeR");'

RUN mkdir jupyter
COPY scripts jupyter
WORKDIR jupyter

ENTRYPOINT jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser --NotebookApp.iopub_data_rate_limit=10000000000 --c.NotebookApp.notebook_dir='jupyter' --NotebookApp.token=