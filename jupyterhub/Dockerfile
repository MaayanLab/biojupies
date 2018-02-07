FROM jupyter/base-notebook:27ba57364579
RUN pip install jupyterhub==0.8
RUN pip install numpy
RUN pip install pandas
RUN pip install jupyter
RUN pip install scipy
RUN pip install seaborn
RUN pip install sklearn
RUN pip install clustergrammer-widget
RUN pip install plotly

USER root
RUN echo deb http://cloud.r-project.org/bin/linux/ubuntu xenial/ >> /etc/apt/sources.list
RUN apt-get update && apt-get install --allow-unauthenticated -y r-base
RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("limma");'
RUN Rscript -e 'source("https://bioconductor.org/biocLite.R"); biocLite("edgeR");'
USER $NB_USER

RUN pip install rpy2
RUN pip install jupyter_contrib_nbextensions
RUN jupyter contrib nbextension install --user
RUN jupyter nbextension enable codefolding/main
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension
RUN jupyter nbextension enable --py --sys-prefix clustergrammer_widget