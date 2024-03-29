#!/usr/bin/env bash

root=/biojupies
user=r
sslroot=/ssl

echo "Booting..."

if [ ! -z "$APPLICATION_DEFAULT_CREDENTIALS" -a ! -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
echo "Initializing gcloud credentials..."
mkdir -p .config/gcloud
echo $APPLICATION_DEFAULT_CREDENTIALS > $GOOGLE_APPLICATION_CREDENTIALS
fi


if [ ! -z "${SSL_CERTIFICATE}" -a ! -z "${SSL_CERTIFICATE_KEY}" ]; then
    echo "Writing SSL Keys..." >> $log
    mkdir -p "${sslroot}"
    echo "${SSL_CERTIFICATE}" | sed 's/;/\n/g' > "${sslroot}/cert.crt"
    echo "${SSL_CERTIFICATE_KEY}" | sed 's/;/\n/g' > "${sslroot}/cert.key"
    export SSL=1
else
    export SSL=
fi

echo "Creating user..."
adduser --disabled-password --gecos '' $user

mkdir -p /tmp
chmod 777 -R /tmp

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

    upstream app {
        server 127.0.0.1:8000 fail_timeout=0;
    }

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
            proxy_pass         http://app;
            proxy_redirect     off;
            proxy_set_header   Host \$host;
            proxy_set_header   X-Real-IP \$remote_addr;
            proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host \$server_name;
            proxy_connect_timeout 300;
            proxy_send_timeout    300;
            proxy_read_timeout    300;
            send_timeout          300;
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
            proxy_pass         http://app;
            proxy_redirect     off;
            proxy_set_header   Host \$host;
            proxy_set_header   X-Real-IP \$remote_addr;
            proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host \$server_name;
            proxy_connect_timeout 300;
            proxy_send_timeout    300;
            proxy_read_timeout    300;
            send_timeout          300;
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
[program:gunicorn]
process_name=%(program_name)s_%(process_num)d
numprocs=1
startsecs=1
startretries=5
autostart=true
directory=/biojupies
command=gunicorn -w4 app.app:app
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
