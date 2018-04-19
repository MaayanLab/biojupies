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
RUN pip3 install google-cloud
RUN pip3 install h5py

RUN apt-get update && apt-get install -y nginx
RUN pip3 install uwsgi
RUN apt-get update && apt-get install -y systemd

RUN mkdir biojupies
COPY . /biojupies
WORKDIR /biojupies/flask

ENTRYPOINT mkdir ~/.config; mkdir ~/.config/gcloud; echo $APPLICATION_DEFAULT_CREDENTIALS > ~/.config/gcloud/application_default_credentials.json; mv app.service /etc/systemd/system; /bin/bash