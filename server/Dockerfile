FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

COPY pkglist.txt .
RUN apt-get update && apt-get install -y $(cat pkglist.txt)

RUN mkdir /notebook-generator-server; virtualenv -p /usr/bin/python3 /notebook-generator-server/venv/;

COPY requirements.R .
RUN Rscript requirements.R

COPY requirements.txt .
RUN . /notebook-generator-server/venv/bin/activate && pip3 install -r requirements.txt
RUN . /notebook-generator-server/venv/bin/activate && python -m ipykernel install --user --name venv --display-name "python3-venv"

ENV LIBRARY_VERSION=v1.1.4

COPY . /notebook-generator-server  
WORKDIR /notebook-generator-server
RUN chmod +x boot.sh download_library.sh; ./download_library.sh

ENTRYPOINT mkdir -p .config/gcloud; echo $APPLICATION_DEFAULT_CREDENTIALS > $GOOGLE_APPLICATION_CREDENTIALS; ./boot.sh