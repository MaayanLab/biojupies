FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev
RUN apt-get update && apt-get install -y curl

RUN pip3 install --upgrade pip
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install Flask
RUN pip3 install pyyaml
RUN pip3 install nbformat
RUN pip3 install kubernetes

RUN mkdir /root/.kube

RUN mkdir notebook-generator
COPY . /notebook-generator
WORKDIR notebook-generator/flask

ENTRYPOINT curl $kubeconfig > /root/.kube/config; curl $google_credentials > $GOOGLE_APPLICATION_CREDENTIALS; python3 __init__.py;