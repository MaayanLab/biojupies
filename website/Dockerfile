FROM ubuntu:18.04

MAINTAINER Denis Torre <denis.torre@mssm.com>

COPY pkglist.txt .
RUN apt-get update && apt-get install -y $(cat pkglist.txt)

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN mkdir biojupies
COPY . /biojupies
WORKDIR /biojupies
RUN chmod +x boot.sh; chmod -R 777 /biojupies/app/static;

ENTRYPOINT mkdir -p .config/gcloud; echo $APPLICATION_DEFAULT_CREDENTIALS > $GOOGLE_APPLICATION_CREDENTIALS; ./boot.sh