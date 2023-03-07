from kubernetes import client
from kubernetes.client.rest import ApiException
from InitData import InitData
import base64


class SecretsManagementCreate(InitData):
    def __init__(self, auth_dict):
        # TODO Add constructor params, atm empty
        super(SecretsManagementCreate, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    @staticmethod
    def secret_object(secret_name, data):
        '''
        :param secret_name:
        :param data: (Eg: "data":{"username":"admin", "password":"test"}}
        :param namespace:
        :return:
        '''

        data = {key: base64.b64encode((value.encode('utf-8'))).decode('utf-8') for (key, value) in data.items()}
        secret_obj = client.V1Secret(metadata=client.V1ObjectMeta(name=secret_name), type='Opaque', data=data)
        return secret_obj

    def create_secret(self, secret_name, namespace, secret_obj, patch=True):
        '''Create secret
        :param secret_name:
        :param namespace:
        :param secret_obj:
        :param patch:
        :return:
        '''

        try:
            api_response = self.v1.create_namespaced_secret(namespace=namespace, body=secret_obj)
            dat = api_response
        except ApiException as e:
            if e.status == 409 and patch:
                # 409 error message is for Conflict, patch the storage class if patch is true
                # btw, we love EAFP :P
                try:
                    api_response = self.v1.patch_namespaced_secret(name=secret_name, body=secret_obj,
                                                                   namespace=namespace)
                    dat = api_response
                except ApiException as e:
                    dat = 'issue patching secret:{0}'.format(e)
            else:
                dat = 'issue creating  secret volume {0}'.format(e)
        return dat


class SecretsManagementDelete(InitData):
    def __init__(self, auth_dict):
        # TODO Add constructor params, atm empty
        super(SecretsManagementDelete, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def delete_secret(self, secret_name, namespace=None):
        '''Delete secret
        :param secret_name:
        :param namespace:
        :return:
        '''

        try:
            if namespace is None:
                namespace = 'default'

            api_response = self.v1.delete_namespaced_secret(name=secret_name, namespace=namespace,
                                                            body=client.V1DeleteOptions(
                                                                propagation_policy='Foreground',
                                                                grace_period_seconds=5))
            dat = api_response
        except ApiException as e:
            dat = 'Issue:{0} deleting secret:{1}'.format(e, secret_name)
        return dat
