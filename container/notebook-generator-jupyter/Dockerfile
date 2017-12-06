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

RUN pip3 install watchdog
RUN pip3 install jupyter_contrib_nbextensions
RUN jupyter contrib nbextension install --user
RUN jupyter nbextension enable hide_input_all/main
RUN jupyter nbextension enable init_cell/main

RUN mkdir jupyter
WORKDIR jupyter
RUN mkdir scripts
COPY notebook-generator-listener.py .
COPY scripts scripts

ENTRYPOINT ln -s /notebook-generator notebook-generator; mv scripts notebook-generator; nohup python3 -u notebook-generator-listener.py > nohup.out & jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser --NotebookApp.iopub_data_rate_limit=10000000000 --NotebookApp.token=