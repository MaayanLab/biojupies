FROM ubuntu:18.04

MAINTAINER Denis Torre <denis.torre@mssm.com>

COPY pkglist.txt .
RUN apt-get update && apt-get install -y $(cat pkglist.txt)

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN set -x \
  && curl https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 > /usr/bin/cloud_sql_proxy \
  && chmod +x /usr/bin/cloud_sql_proxy \
  && mkdir /cloudsql \
  && chmod 777 /cloudsql

RUN mkdir biojupies
COPY . /biojupies
WORKDIR /biojupies
RUN chmod +x boot.sh; chmod -R 777 /biojupies/app/static;

CMD ./boot.sh