FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev
RUN apt-get update && apt-get install -y wget

RUN pip3 install --upgrade pip
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install jupyter
RUN pip3 install scipy
RUN pip3 install seaborn
RUN pip3 install sklearn
RUN pip3 install clustergrammer-widget
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension
RUN jupyter nbextension enable --py --sys-prefix clustergrammer_widget

RUN mkdir jupyter
COPY scripts jupyter
COPY start-notebook.sh /usr/local/bin
RUN export JUPYTER_PATH=/jupyter/scripts:$JUPYTER_PATH

RUN chmod 777 /usr/local/bin/start-notebook.sh
ENTRYPOINT /usr/local/bin/start-notebook.sh