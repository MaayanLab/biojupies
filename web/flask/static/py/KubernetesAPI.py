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

#################################################################
#################################################################
############### 1. Deployments ##################################
#################################################################
#################################################################

#############################################
########## 1. Generate Deployment
#############################################

def GeneratePod(username):

	# Load Extension
	v1 = client.CoreV1Api()

	# Add Pod Template
	pod = client.V1Pod()
	pod.metadata = client.V1ObjectMeta(name="notebook-generator-pod-{username}".format(**locals()), labels={"group": "notebook-generator", "username": username})
	pod.spec = client.V1PodSpec()

	# Create Volume
	volume = client.V1Volume()
	volume.name = "notebook-volume"
	volume.emptyDir = client.V1EmptyDirVolumeSource()
	pod.spec.volumes = [volume]

	# Create Volume Mount
	volume_mount = client.V1VolumeMount()
	volume_mount.name = "notebook-volume"
	volume_mount.mount_path = "/notebook-generator"

	# Create Liveness Probe
	# liveness_probe = client.V1Probe()
	# liveness_probe._exec = client.V1ExecAction(['cat', '/notebook-generator/healthy'])
	# liveness_probe.initial_delay_seconds = 5
	# liveness_probe.period_seconds = 5
	# liveness_probe.failure_threshold = 1

	# Create Jupyter Server
	jupyter_container = client.V1Container()
	jupyter_container.name="notebook-generator-jupyter"
	jupyter_container.image="gcr.io/notebook-generator/notebook-generator-jupyter"
	jupyter_container.ports = [client.V1ContainerPort(container_port=8888, host_port=8888)]
	jupyter_container.volume_mounts = [volume_mount]
	# jupyter_container.liveness_probe = liveness_probe

	# Create Notebook Manager
	manager_container = client.V1Container()
	manager_container.name="notebook-generator-manager"
	manager_container.image="gcr.io/notebook-generator/notebook-generator-manager"
	manager_container.ports = [client.V1ContainerPort(container_port=5000, host_port=5000)]
	manager_container.volume_mounts = [volume_mount]
	manager_container.env = [client.V1EnvVar(name='username', value=username)]
	# manager_container.liveness_probe = liveness_probe

	# Add Containers
	pod.spec.containers = [jupyter_container, manager_container]
	# pod.spec.restart_policy = "Never"

	# Create Deployment
	v1.create_namespaced_pod(namespace="default", body=pod)

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
	manager_port = client.V1ServicePort(protocol="TCP", port=5000, target_port=5000)
	manager_port.name = "notebook-generator-manager"

	# Add Ports
	service.spec.ports = [jupyter_port, manager_port]
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
########## 1. Launch Pod
#############################################

def LaunchPod(username):
	
	# Load Config
	config.load_kube_config()

	# Check IP
	checked_ip = CheckServiceIP(username)

	# Get IP
	if checked_ip:
		service_ip = checked_ip
	else:
		try:
			GeneratePod(username)
			GenerateService(username)
		except:
			pass
		service_ip = GetServiceIP(username)
	return service_ip

#############################################
########## 2. Launch Service
#############################################

def GetServiceStatus(username):

	# Load Config
	config.load_kube_config()

	# Create API Instance
	api_instance = client.CoreV1Api()

	# Get Services
	services = api_instance.list_service_for_all_namespaces()

	# Get Service
	service = [x for x in services.to_dict()['items'] if x['metadata']['name']=='notebook-generator-service-maayanlab']

	# Get Status
	if len(service) == 0:
		service_status = 'offline'
	else:
		load_balancer = service[0]['status']['load_balancer']['ingress']
		if type(load_balancer) == list:
			service_status = load_balancer[0]['ip']
		else:
			service_status = 'launching'

	return service_status

#############################################
########## 3. Stop Service
#############################################

def StopService(username):

	# Load Config
	config.load_kube_config()

	# Create API Instance
	api_instance = client.CoreV1Api()

	# Delete Pod and Service
	try:
		api_response = api_instance.delete_namespaced_pod(name='notebook-generator-pod-{username}'.format(**locals()), namespace='default', body=client.V1DeleteOptions())
		api_response = api_instance.delete_namespaced_service(name='notebook-generator-service-{username}'.format(**locals()), namespace='default')
		response = 'deletion success'
	except:
		response = 'deletion error'

	# Stop
	return response
