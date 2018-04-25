#!/usr/bin/env bash

root=/notebook-generator-server
user=root
log=$root/error.log

function setup {

echo "Creating user..." >> $log
adduser --disabled-password --gecos '' $user >> $log

echo "Writing wsgi.ini..." >> $log
cat << EOF | tee -a $root/wsgi.ini >> $log
[uwsgi]
uid = $user
gid = $user

home = /notebook-generator-server/venv
plugins = python3

master = true
processes = 5

chdir = $root
wsgi-file = $root/wsgi.py

socket = 127.0.0.1:8080
daemonize = $log
EOF

echo "Writing nginx.conf..." >> $log
cat << EOF | tee -a $root/nginx.conf >> $log
user $user $user;

worker_processes 1;

events {
	worker_connections 1024;
}

http {
    access_log $log;
	error_log $log;

	gzip              on;
	gzip_http_version 1.0;
	gzip_proxied      any;
	gzip_min_length   500;
	gzip_disable      "MSIE [1-6]\.";
	gzip_types        text/plain text/xml text/css
					  text/comma-separated-values
					  text/javascript
					  application/x-javascript
					  application/atom+xml;

    server {
        listen 80;
        charset utf-8;
        client_max_body_size 20M;
        sendfile on;
        keepalive_timeout 0;
        large_client_header_buffers 8 32k;

        location /static  {
            alias $root/app/static;
        }

        location / {
            include            /etc/nginx/uwsgi_params;
            uwsgi_pass         127.0.0.1:8080;
            proxy_redirect     off;
            proxy_set_header   Host \$host;
            proxy_set_header   X-Real-IP \$remote_addr;
            proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host \$server_name;
            uwsgi_read_timeout 120; 
        }
    }
}
EOF

echo "Starting uwsgi..." >> $log
uwsgi --ini $root/wsgi.ini >> $log

echo "Starting nginx..." >> $log
nginx -c $root/nginx.conf >> $log

}

if [ -f $log ]; then
    rm $log;
fi

echo "Booting..." > $log
setup &

tail -f $log