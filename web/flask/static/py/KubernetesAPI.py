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

def GenerateDeployment(username):

	# Load Extension
	extension = client.ExtensionsV1beta1Api()

	# Create Deployment Object
	deployment = client.ExtensionsV1beta1Deployment()

	# Fill Required Fields (apiVersion, kind, metadata)
	deployment.api_version = "extensions/v1beta1"
	deployment.kind = "Deployment"
	deployment.metadata = client.V1ObjectMeta(name="notebook-generator-deployment-{username}".format(**locals()), labels={"group": "notebook-generator", "username": username})

	# Add Spec
	deployment.spec = client.ExtensionsV1beta1DeploymentSpec()
	deployment.spec.replicas = 1

	# Add Pod Template
	deployment.spec.template = client.V1PodTemplateSpec()
	deployment.spec.template.metadata = client.V1ObjectMeta(labels={"app": "notebook-generator", "username": username})
	deployment.spec.template.spec = client.V1PodSpec()

	# Create Volume
	volume = client.V1Volume()
	volume.name = "notebook-volume"
	volume.emptyDir = client.V1EmptyDirVolumeSource()
	deployment.spec.template.spec.volumes = [volume]

	# Create Volume Mount
	volume_mount = client.V1VolumeMount()
	volume_mount.name = "notebook-volume"
	volume_mount.mount_path = "/notebooks"

	# Create Jupyter Server
	jupyter_container = client.V1Container()
	jupyter_container.name="notebook-generator-jupyter"
	jupyter_container.image="gcr.io/notebook-generator/notebook-generator-jupyter"
	jupyter_container.ports = [client.V1ContainerPort(container_port=8888, host_port=8888)]
	jupyter_container.volume_mounts = [volume_mount]

	# Create Notebook Manager
	manager_container = client.V1Container()
	manager_container.name="notebook-generator-manager"
	manager_container.image="gcr.io/notebook-generator/notebook-generator-manager"
	manager_container.ports = [client.V1ContainerPort(container_port=5000, host_port=5000)]
	manager_container.volume_mounts = [volume_mount]
	manager_container.env = [client.V1EnvVar(name='username', value=username)]

	# Add Containers
	deployment.spec.template.spec.containers = [jupyter_container, manager_container]

	# Create Deployment
	extension.create_namespaced_deployment(namespace="default", body=deployment)

#############################################
########## 2. Generate Service
#############################################

def GenerateService(username):

	# Create API Endpoint and Resources
	api_instance = client.CoreV1Api()
	service = client.V1Service()

	# Fill Required Fields (apiVersion, kind, metadata)
	service.api_version = "v1"
	service.kind = "Service"
	service.metadata = client.V1ObjectMeta(name="notebook-generator-service-{username}".format(**locals()), labels={"group": "notebook-generator", "username": username})

	# Add Spec
	service.spec = client.V1ServiceSpec()
	service.spec.selector = {"app": "notebook-generator", "username": username}

	# Create Ports
	jupyter_port = client.V1ServicePort(protocol="TCP", port=8888, target_port=8888)
	jupyter_port.name = "notebook-generator-jupyter"
	downloader_port = client.V1ServicePort(protocol="TCP", port=5000, target_port=5000)
	downloader_port.name = "notebook-generator-manager"

	# Add Ports
	service.spec.ports = [jupyter_port, downloader_port]
	service.spec.type = "LoadBalancer"

	# Create Service
	api_instance.create_namespaced_service(namespace="default", body=service)

#############################################
########## 3. Check Service IP
#############################################

def CheckServiceIP(username):

	# Initialize Service IP
	service_ip = None

	# Create API Instance
	api_instance = client.CoreV1Api()

	# Check if Service Exists
	services = [x.to_dict() for x in api_instance.list_namespaced_service("default").items]

	# Loop through services
	for service in services:
		if service['metadata']['labels'].get('username') == username:
			ingress_loadbalancer = service['status']['load_balancer']['ingress']
			if type(ingress_loadbalancer) == list:
				service_ip = ingress_loadbalancer[0].get('ip')

	return service_ip

#############################################
########## 4. Get Service IP
#############################################

def GetServiceIP(username, check=True):

	# Create API Instance
	api_instance = client.CoreV1Api()

	# Run a Watch
	w = watch.Watch()
	for event in w.stream(api_instance.list_service_for_all_namespaces):
		if event['raw_object']['metadata']['name']=='notebook-generator-service-{username}'.format(**locals()) and type(event['raw_object']['status']['loadBalancer'].get('ingress')) == list:
			ip = event['raw_object']['status']['loadBalancer']['ingress'][0]['ip']
			break

	# Return IP
	return ip

#################################################################
#################################################################
############### 2. Wrapper ######################################
#################################################################
#################################################################

#############################################
########## 1. Launch Deployment
#############################################

def LaunchDeployment(username):

	# Check IP
	checked_ip = CheckServiceIP(username)

	# Get IP
	if checked_ip:
		service_ip = checked_ip
	else:
		try:
			GenerateDeployment(username)
			GenerateService(username)
		except:
			pass
		service_ip = GetServiceIP(username)
	return service_ip
