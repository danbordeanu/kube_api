from kubernetes import client
from kubernetes.client.rest import ApiException
from InitData import InitData


# handling new service
class ServicesManagementCreate(InitData):
    def __init__(self, auth_dict, deployment_name, port, protocol, target_port):
        super(ServicesManagementCreate, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''
        # Configure the service ports and protocol
        self.service_port = client.V1ServicePort(name=str(port), port=int(port), protocol=protocol,
                                                 target_port=int(target_port))

        # Create the specification of the deployment
        self.spec = client.V1ServiceSpec(ports=[self.service_port], type='LoadBalancer',
                                         selector={'app': deployment_name})

    def create_service_object(self, service_name):
        '''
        :param service_name:
        :return:
        '''

        # Instantiate the service object
        service = client.V1Service(kind='Service', metadata=client.V1ObjectMeta(
            annotations={'service.beta.kubernetes.io/azure-load-balancer-internal': 'true'}, name=service_name),
                                   spec=self.spec)

        return service

    def create_service(self, service, namespace_name):
        '''
        :param service:
        :param namespace_name:
        :return:
        '''
        try:
            api_response = self.v1.create_namespaced_service(
                namespace=namespace_name,
                body=service)
            dat = api_response
        except ApiException as e:
            dat = 'Issue:{0} creating service:{1}'.format(e, service)
        return dat

    def patch_service(self, service, service_name, namespace_name):
        '''
        :param service:
        :param service_name
        :param namespace_name:
        :return:
        '''
        try:
            api_response = self.v1.patch_namespaced_service(name=service_name,
                                                            namespace=namespace_name,
                                                            body=service)
            dat = api_response
        except ApiException as e:
            dat = 'Issue:{0} patching service:{1}'.format(e, service)
        return dat


# handling service delete
class ServicesManagementDelete(InitData):
    def __init__(self, auth_dict):
        super(ServicesManagementDelete, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def delete_service(self, service, namespace=None):
        '''
        Delete service
        :param service:
        :param namespace
        :return:
        '''
        try:
            # if namespace is not provided we assume it will be the default namespace
            if namespace is None:
                namespace = 'default'

            api_response = self.v1.delete_namespaced_service(name=service, body=client.V1DeleteOptions(),
                                                             namespace=namespace)
            dat = api_response.status
        except ApiException as e:
            dat = 'Issue:{0} deleting service:{1}'.format(e, service)
        return dat


# handling read service info
class ServicesManagementRead(InitData):
    def __init__(self, auth_dict):
        super(ServicesManagementRead, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def read_service(self, service, namespace=None):
        '''
        Delete service
        :param service:
        :param namespace
        :return:
        '''
        try:
            # if namespace is not provided we assume it will be the default namespace
            if namespace is None:
                namespace = 'default'

            api_response = self.v1.read_namespaced_service(name=service, namespace=namespace)
            dat = str(api_response)
        except ApiException as e:
            dat = 'Issue:{0} reading service:{1}'.format(e, service)
        return dat
