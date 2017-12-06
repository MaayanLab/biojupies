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

RUN mkdir flask
COPY flask flask
WORKDIR flask

ENTRYPOINT ln -s /notebook-generator notebook-generator; python3 __init__.py;