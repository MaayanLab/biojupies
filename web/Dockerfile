FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev

RUN apt-get update && apt-get install -y curl
RUN apt-get update && apt-get install -y lsb-release
RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
RUN echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt-get install -y google-cloud-sdk
RUN apt-get update && apt-get install -y kubectl

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

