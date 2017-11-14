FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev
RUN apt-get update && apt-get install -y libmysqlclient-dev
RUN apt-get update && apt-get install -y curl

RUN pip3 install --upgrade pip
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install Flask
RUN pip3 install nbformat
RUN pip3 install sqlalchemy
RUN pip3 install flask-sqlalchemy
RUN pip3 install kubernetes
RUN pip3 install google-cloud
RUN pip3 install mysqlclient

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

RUN mkdir notebook-generator-web
COPY . /notebook-generator-web
RUN chmod +x /notebook-generator-web/config.sh
WORKDIR notebook-generator-web/flask

ENTRYPOINT ../config.sh; python3 __init__.py