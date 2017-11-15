kubectl config set-cluster notebook-generator-cluster --insecure-skip-tls-verify=true --server=$SERVER
kubectl config set-credentials notebook-generator-user --username=$USERNAME --password=$PASSWORD
kubectl config set-context notebook-generator-context --namespace=default --user=notebook-generator-user --cluster=notebook-generator-cluster
kubectl config use-context notebook-generator-context

export GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS
echo $CREDENTIALS > $GOOGLE_APPLICATION_CREDENTIALS

ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
dpkg-reconfigure --frontend noninteractive tzdata