FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev

RUN pip3 install --upgrade pip
RUN pip3 install flask
RUN pip3 install nbformat
RUN pip3 install nbconvert
RUN pip3 install requests

RUN pip3 install jupyter
RUN pip3 install scipy
RUN pip3 install seaborn
RUN pip3 install sklearn
RUN pip3 install clustergrammer-widget
RUN pip3 install plotly
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension
RUN jupyter nbextension enable --py --sys-prefix clustergrammer_widget

RUN pip3 install watchdog

RUN mkdir flask
COPY notebook-generator-listener.py flask
COPY flask flask
WORKDIR flask

ENTRYPOINT ln -s /notebook-generator notebook-generator; touch /notebook-generator/healthy; nohup python3 -u notebook-generator-listener.py > nohup.out & disown; python3 __init__.py;