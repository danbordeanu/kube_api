from kubernetes import client
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint


# see https://kubernetes.io/docs/tasks/administer-cluster/access-cluster-api/#accessing-the-cluster-api to know how to get the token
# The command look like kubectl get secrets | grep default | cut -f1 -d ' ') | grep -E '^token' | cut -f2 -d':' | tr -d '\t' but better check the official doc link
aToken = 'token'

#configuration.username = "admin"
#configuration.password = "XXXXXXXXXXX"

# Configs can be set in Configuration class directly or using helper utility
configuration = client.Configuration()
configuration.host = "https://aksclu-.hcp.eastus.azmk8s.io:443"
configuration.verify_ssl = True

# take the base64 string from config and decode it and put it into a file
configuration.ssl_ca_cert = '../ca_cert.crt'
configuration.debug = False



configuration.api_key['authorization'] = aToken
configuration.api_key_prefix['authorization'] = 'Bearer'
configuration.api_key['context'] = 'aksclu01'

configuration.api_key
# return api key

#print configuration.get_api_key_with_prefix('authorization')

client.Configuration.set_default(configuration)



#listnamespaces

print 'namespaces:'
v1 = client.CoreV1Api(client.ApiClient(configuration))
print v1.list_namespace(pretty=True, watch=False)



# list pods

v1 = client.CoreV1Api(client.ApiClient(configuration))
print('Listing pods with their IPs:')
print v1.list_namespace()
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

# registration api
api_instance = kubernetes.client.AdmissionregistrationApi()

try:
    api_response = api_instance.get_api_group()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AdmissionregistrationApi->get_api_group: %s\n" % e)

# create a namespace

# try:
#     print 'creating a namespace'
#     body = client.V1Namespace()
#     body.metadata = client.V1ObjectMeta(name='ns-staging')
#     v1.create_namespace(body)
# except ApiException as e:
#     print ('Some issue creating the name space:{0}'.format(e))
#
# # apply quata on this namespace
#
#
# print 'apply limits'
#
# resource_quota = client.V1ResourceQuota(spec=client.V1ResourceQuotaSpec(
#             hard={"requests.cpu": "1", "requests.memory": "512M", "limits.cpu": "2", "limits.memory": "512M",
#                 "requests.storage": "1Gi", "services.nodeports": "0"}))
# resource_quota.metadata = client.V1ObjectMeta(namespace="ns-staging", name="user-quota")
#
# v1.create_namespaced_resource_quota("ns-staging", resource_quota)
#
#
#
#
# # # list namespaces
# # print 'all namespaces:'
# # print v1.list_namespace(pretty=True, watch=False)
# #
# # delete a namespace
try:
    print 'delete a namespace'
    v1.delete_namespace(name='ns-staging', body=client.V1DeleteOptions())
except ApiException as e:
    print ('Some issue deleting the name space:{0}'.format(e))


