FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python
RUN apt-get update && apt-get install -y python-pip
RUN apt-get update && apt-get install -y python-dev
RUN apt-get update && apt-get install -y libmysqlclient-dev

RUN pip install numpy
RUN pip install pandas
RUN pip install Flask
RUN pip install sqlalchemy
RUN pip install flask-sqlalchemy
RUN pip install mysql-python
RUN pip install nbformat
RUN pip install nbconvert

RUN mkdir notebook-generator-server
COPY . /notebook-generator-server
WORKDIR /notebook-generator-server/flask

ENTRYPOINT python __init__.py