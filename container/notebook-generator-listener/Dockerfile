FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev

RUN pip3 install --upgrade pip

RUN mkdir py
COPY py py
WORKDIR py

ENTRYPOINT python3 notebook-generator-listener.py