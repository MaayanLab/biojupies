#!/usr/bin/env bash

root=/biojupies
user=r

echo "Booting..."

if [ ! -z "$APPLICATION_DEFAULT_CREDENTIALS" -a ! -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
echo "Initializing gcloud credentials..."
mkdir -p .config/gcloud
echo $APPLICATION_DEFAULT_CREDENTIALS > $GOOGLE_APPLICATION_CREDENTIALS
fi

echo "Creating user..."
adduser --disabled-password --gecos '' $user

mkdir -p /tmp
chmod 777 -R /tmp

echo "Writing wsgi.ini..."
cat << EOF | tee -a $root/wsgi.ini
[uwsgi]
uid = $user
gid = $user

enable-threads = true

master = true
processes = 5

chdir = $root
wsgi-file = $root/wsgi.py

socket = /tmp/uwgsi.sock
chmod-socket = 666
EOF

echo "Writing nginx.conf..."
cat << EOF | tee -a $root/nginx.conf
user $user $user;

worker_processes 1;

events {
	worker_connections 1024;
}

http {
#	access_log /dev/stdout;
	error_log /dev/stderr;

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
        client_max_body_size 30M;
        sendfile on;
        keepalive_timeout 0;
        large_client_header_buffers 8 32k;
        location /static  {
            alias $root/app/static;
        }
        location / {
            include            /etc/nginx/uwsgi_params;
            uwsgi_pass         unix:///tmp/uwgsi.sock;
            proxy_redirect     off;
            proxy_set_header   Host \$host;
            proxy_set_header   X-Real-IP \$remote_addr;
            proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host \$server_name;
        }
    }
EOF

if [ ! -z "${SSL}" ]; then

cat << EOF | tee -a $root/nginx.conf

    server {
        listen 443 default ssl;

        # ssl on;
        ssl_certificate $sslroot/cert.crt;
        ssl_certificate_key $sslroot/cert.key;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_prefer_server_ciphers on;
        ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';

        include /etc/nginx/mime.types;
        charset utf-8;
        client_max_body_size 30M;
        sendfile on;
        keepalive_timeout 0;
        large_client_header_buffers 8 32k;

        location /static  {
            alias $root/app/static;
        }

        location / {
            include            /etc/nginx/uwsgi_params;
            uwsgi_pass         unix:///tmp/uwgsi.sock;
            proxy_redirect     off;
            proxy_set_header   Host \$host;
            proxy_set_header   X-Real-IP \$remote_addr;
            proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host \$server_name;
        }
    }
EOF

fi

cat << EOF | tee -a $root/nginx.conf
}
EOF

echo "Writing supervisord.conf..."
cat << EOF | tee -a $root/supervisord.conf
[supervisord]

EOF

if [ ! -z "$SQL_INSTANCE_CONNECTION_NAME" ]; then

echo "Configuring google cloud proxy..."

cat << EOF | tee -a $root/supervisord.conf
[program:cloud_sql_proxy]
process_name=%(program_name)s_%(process_num)d
numprocs=1
startsecs=0
startretries=5
autostart=true
command=/usr/bin/cloud_sql_proxy -instances=$SQL_INSTANCE_CONNECTION_NAME=tcp:3306
autorestart=true
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
EOF

fi

cat << EOF | tee -a $root/supervisord.conf
[program:uwsgi]
process_name=%(program_name)s_%(process_num)d
numprocs=1
startsecs=1
startretries=5
autostart=true
command=uwsgi --ini $root/wsgi.ini
autorestart=true
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0

[program:nginx]
process_name=%(program_name)s_%(process_num)d
numprocs=1
startsecs=2
startretries=5
autostart=true
command=nginx -c $root/nginx.conf -g "daemon off;"
autorestart=true
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0

[eventlistener:processes]
command=bash -c "printf 'READY\n' && while read line; do kill -SIGQUIT \$PPID; done < /dev/stdin"
events=PROCESS_STATE_STOPPED, PROCESS_STATE_EXITED, PROCESS_STATE_FATAL
EOF

echo "Starting supervisord..."
supervisord -nc $root/supervisord.conf
