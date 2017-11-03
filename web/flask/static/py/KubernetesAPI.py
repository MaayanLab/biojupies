#################################################################
#################################################################
############### Notebook Generator ##############################
#################################################################
#################################################################
##### Author: Denis Torre
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#################################################################
#################################################################
############### 1. Library Configuration ########################
#################################################################
#################################################################

#############################################
########## 1. Load libraries
#############################################
##### 1. Python modules #####
from kubernetes import client, config, watch
config.load_kube_config()

#################################################################
#################################################################
############### 1. Deployments ##################################
#################################################################
#################################################################

#############################################
########## 1. Generate Deployment
#############################################

def GenerateDeployment(notebook_url, acc):

	# Load Extension
	extension = client.ExtensionsV1beta1Api()

	# Create Deployment Object
	deployment = client.ExtensionsV1beta1Deployment()

	# Fill Required Fields (apiVersion, kind, metadata)
	deployment.api_version = "extensions/v1beta1"
	deployment.kind = "Deployment"
	deployment.metadata = client.V1ObjectMeta(name="notebook-generator-deployment-{acc}".format(**locals()), labels={"group": "notebook-generator"})

	# Add Spec
	deployment.spec = client.ExtensionsV1beta1DeploymentSpec()
	deployment.spec.replicas = 1

	# Add Pod Template
	deployment.spec.template = client.V1PodTemplateSpec()
	deployment.spec.template.metadata = client.V1ObjectMeta(labels={"app": "notebook-generator-{acc}".format(**locals())})
	deployment.spec.template.spec = client.V1PodSpec()

	# Add Container
	container = client.V1Container()
	container.name="notebook-generator-container"
	container.image="gcr.io/notebook-generator/notebook-generator"
	container.ports = [client.V1ContainerPort(container_port=8888)]
	container.env = [client.V1EnvVar(name='DOWNLOAD', value=notebook_url)]
	deployment.spec.template.spec.containers = [container]

	# Create Deployment
	extension.create_namespaced_deployment(namespace="default", body=deployment)

#################################################################
#################################################################
############### 2. Services #####################################
#################################################################
#################################################################

#############################################
########## 1. Generate Service
#############################################

def GenerateService(acc):

	# Create API Endpoint and Resources
	api_instance = client.CoreV1Api()
	service = client.V1Service()

	# Fill Required Fields (apiVersion, kind, metadata)
	service.api_version = "v1"
	service.kind = "Service"
	service.metadata = client.V1ObjectMeta(name="notebook-generator-service-{acc}".format(**locals()), labels={"group": "notebook-generator"})

	# Add Spec
	service.spec = client.V1ServiceSpec()
	service.spec.selector = {"app": "notebook-generator-{acc}".format(**locals())}
	service.spec.ports = [client.V1ServicePort(protocol="TCP", port=8888, target_port=8888)]
	service.spec.type = "LoadBalancer"

	# Create Service
	api_instance.create_namespaced_service(namespace="default", body=service)

#############################################
########## 2. Watch Service
#############################################

def WatchService(acc):

	# Create API Instance
	api_instance = client.CoreV1Api()

	# Run a Watch
	w = watch.Watch()
	for event in w.stream(api_instance.list_service_for_all_namespaces):
		if event['type'] == 'MODIFIED' and event['raw_object']['metadata']['name']=='notebook-generator-service-{acc}'.format(**locals()) and len(event['raw_object']['status']['loadBalancer']['ingress']) > 0:
			ip = event['raw_object']['status']['loadBalancer']['ingress'][0]['ip']
			break

	# Get URL
	url = 'http://'+ip+':8888'

	# Return IP
	return url
