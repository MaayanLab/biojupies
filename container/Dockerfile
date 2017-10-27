FROM ubuntu:17.10

MAINTAINER Denis Torre <denis.torre@mssm.com>

RUN apt-get update && apt-get install -y python3
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y python3-dev
RUN apt-get update && apt-get install -y wget

RUN pip3 install --upgrade pip
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install jupyter

RUN mkdir jupyter
COPY start-notebook.sh /usr/local/bin
RUN chmod 777 /usr/local/bin/start-notebook.sh
ENTRYPOINT /usr/local/bin/start-notebook.sh