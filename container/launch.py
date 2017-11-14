#############################################
########## 1. Load Libraries
#############################################
from kubernetes import client, config
config.load_kube_config()

#############################################
########## 2. Generate Deployment
#############################################
# Load Extension
extension = client.ExtensionsV1beta1Api()

# Create Deployment Object
deployment = client.ExtensionsV1beta1Deployment()

# Fill Required Fields (apiVersion, kind, metadata)
deployment.api_version = "extensions/v1beta1"
deployment.kind = "Deployment"
deployment.metadata = client.V1ObjectMeta(name="notebook-generator-deployment", labels={"group": "notebook-generator"})

# Add Spec
deployment.spec = client.ExtensionsV1beta1DeploymentSpec()
deployment.spec.replicas = 1

# Add Pod Template
deployment.spec.template = client.V1PodTemplateSpec()
deployment.spec.template.metadata = client.V1ObjectMeta(labels={"app": "notebook-generator"})
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

# Add Containers
deployment.spec.template.spec.containers = [jupyter_container, manager_container]

# Create Deployment
extension.create_namespaced_deployment(namespace="default", body=deployment)

#############################################
########## 3. Generate Service
#############################################
# Create API Endpoint and Resources
api_instance = client.CoreV1Api()
service = client.V1Service()

# Fill Required Fields (apiVersion, kind, metadata)
service.api_version = "v1"
service.kind = "Service"
service.metadata = client.V1ObjectMeta(name="notebook-generator-service", labels={"group": "notebook-generator"})

# Add Spec
service.spec = client.V1ServiceSpec()
service.spec.selector = {"app": "notebook-generator".format(**locals())}

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
