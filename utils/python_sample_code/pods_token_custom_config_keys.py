from kubernetes import client
from kubernetes.client.rest import ApiException

# this scrips is using ssl_dev cert to auth against the kube cluster


# Configs can be set in Configuration class directly or using helper utility
configuration = client.Configuration()
configuration.host = 'https://aksclu0.hcp.eastus.azmk8s.io:443'
configuration.verify_ssl = True

# take the base64 string from config and decode it and put it into a file
# this is certificate-authority-data
configuration.ssl_ca_cert = '../ssl_dev/ca_cert.crt'
# this is client-certificate-data
configuration.cert_file = '../ssl_dev/cert_file.crt'
# this is client-key-data
configuration.key_file = '../ssl_dev/key_file.crt'
configuration.debug = False

configuration.api_key['context'] = 'aksclu01'

client.Configuration.set_default(configuration)

v1 = client.CoreV1Api(client.ApiClient(configuration))
api_instance = client.AppsV1Api(client.ApiClient(configuration))
storage = client.StorageV1Api(client.ApiClient(configuration))


# listnamespaces

# print 'namespaces:'
# print v1.list_namespace(pretty=True, watch=False)
#
# # list deployments
# api_response = api_instance.list_namespaced_deployment('ns-staging')
# #print(api_response)
# for deployment in api_response.items:
#     #print replicas
#     print deployment.spec.replicas

# list pods


# pod_list = v1.list_namespaced_pod('ns-staging')
# for pod in pod_list.items:
#     print("%s\t%s\t%s" % (pod.metadata.name,
#                             pod.status.phase,
#                             pod.status.pod_ip))

# create service


# deployment_name = 'nginx-deploy'
#
# print 'create deploy:{0}'.format(deployment_name)
#
# service_port = client.V1ServicePort(name='80', port=80, protocol='TCP', target_port=80)
#
#
# spec = client.V1ServiceSpec(ports=[service_port], type='LoadBalancer', selector={'app': deployment_name})
#
# service = client.V1Service(kind='Service', metadata=client.V1ObjectMeta(name='nginx-service'), spec=spec)
#
# print service
#
#
# api_response = v1.create_namespaced_service(
#             namespace='ns-staging',
#             body=service)
# print api_response.status

# create ingress

# def create_ingress_object():
#
#     bakends = client.V1beta1IngressBackend(
#             service_name='nginx-service',
#             service_port=80
#         )
#
#     paths = client.V1beta1HTTPIngressPath(
#             backend=bakends,
#             path='/')
#
#     http = client.V1beta1HTTPIngressRuleValue(paths=[paths])
#     rule = client.V1beta1IngressRule(http=http)
#     spec = client.V1beta1IngressSpec(rules=[rule])
#
#     ingress = client.V1beta1Ingress(
#         api_version="extensions/v1beta1",
#         kind='Ingress',
#         metadata=client.V1ObjectMeta(name='nginx-ingress'),
#         spec=spec)
#     return ingress
#
#
# def create_ingress():
#     ingress_obj = create_ingress_object()
#     print ingress_obj
#     response = client.ExtensionsV1beta1Api().create_namespaced_ingress(
#         namespace="ns-staging",
#         body=ingress_obj)
#     print response
#
#
# create_ingress()

# create storage class

def create_storage_class_object():
    '''
    kind: StorageClass
    apiVersion: storage.k8s.io/v1
    metadata:
      name: azurefile
    provisioner: kubernetes.io/azure-file
    mountOptions:
      - dir_mode=0777
      - file_mode=0777
      - uid=1000
      - gid=1000
    parameters:
      skuName: Standard_LRS
    '''

    storage_obj = client.V1StorageClass(api_version='storage.k8s.io/v1',
                                        metadata=client.V1ObjectMeta(name='nginx-storage', namespace='ns-staging'),
                                        mount_options=["dir_mode=0777", "file_mode=0777", "uid=1000", "gid=1000"],
                                        parameters={'skuName': 'Standard_LRS'},
                                        provisioner='kubernetes.io/azure-file',
                                        kind='StorageClass'
                                        )
    return storage_obj


def create_storage_class():
    storage_obj = create_storage_class_object()
    try:
        storage.create_storage_class(body=storage_obj)
        print 'storage class created'
    except ApiException as e:
        if e.status == 409:
            print 'class already exists..patching'
            try:
                storage.patch_storage_class(name='nginx-storage', body=storage_obj)
            except ApiException as e:
                print 'issue patching the storage class:{0}'.format(e)
        else:
            print 'issue creating storage class:{0}'.format(e)


def persistent_volume():
    """Create persistent volume by default on host."""
    spec = client.V1PersistentVolumeSpec(capacity={'storage': '2Gi'}, access_modes=['ReadWriteMany'],
                                         storage_class_name='nginx-storage',
                                         host_path=client.V1HostPathVolumeSource(path='/mnt/azure/'),
                                         persistent_volume_reclaim_policy='Delete')

    ps_vol = client.V1PersistentVolume(kind='PersistentVolume', api_version='v1',
                                       metadata=client.V1ObjectMeta(name='nginx-volume-bis', namespace='ns-staging'),
                                       spec=spec)

    try:
        v1.create_persistent_volume(body=ps_vol)
        print 'persistent volume created'
    except ApiException as e:
        if e.status == 409:
            print 'issue creating persistent volume {0}, patching'
            v1.patch_persistent_volume(name='nginx-volume-bis', body=ps_vol)
        else:
            print 'issue patching:{0}'.format(e)


def persistent_volume_claim():
    """Create a volume claim."""
    spec = client.V1PersistentVolumeClaimSpec(access_modes=['ReadWriteMany'],
                                              storage_class_name='nginx-storage',
                                              resources=client.V1ResourceRequirements(requests={'storage': '2Gi'}))

    claim_vol = client.V1PersistentVolumeClaim(kind='PersistentVolumeClaim', api_version='v1',
                                               metadata=client.V1ObjectMeta(name='nginx-volume-bis'), spec=spec)
    try:
        v1.create_namespaced_persistent_volume_claim(namespace='ns-staging', body=claim_vol)
        print 'persistent volume claim created'
    except ApiException as e:
        print 'issue creating volume claim: {0}'.format(e)


create_storage_class()
persistent_volume()
persistent_volume_claim()
