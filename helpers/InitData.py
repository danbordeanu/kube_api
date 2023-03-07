from kubernetes import client
import os
from helpers import logger_settings


class InitData(object):
    def __init__(self, auth_dict):
        '''
        set kubernetes configuration strings
        :param auth_dict:
        '''
        try:
            self.configuration = client.Configuration()
            # kube cluster host
            self.configuration.host = auth_dict['host']
            self.configuration.verify_ssl = True
            # certificate-authority-data
            self.configuration.ssl_ca_cert = auth_dict['ssl_ca_cert_file']
            # client-certificate-data
            self.configuration.cert_file = auth_dict['ssl_cert_file']
            # client-key-data
            self.configuration.key_file = auth_dict['ssl_key_file']
            # http proxy
            self.configuration.proxy = auth_dict['proxy']
            # check if debug env value is True/False to enable debugging
            self.configuration.debug = os.environ.get('KUBE_DEBUG', False)
            # kube cluster context
            self.configuration.api_key['context'] = auth_dict['context']

            self.v1 = client.CoreV1Api(client.ApiClient(self.configuration))
            self.netwpork = client.ExtensionsV1beta1Api(client.ApiClient(self.configuration))
            self.v1_extension = client.AppsV1Api(client.ApiClient(self.configuration))
            self.storage = client.StorageV1Api(client.ApiClient(self.configuration))
            self.scale = client.AutoscalingV1Api(client.ApiClient(self.configuration))
            self.rbac = client.RbacAuthorizationV1Api(client.ApiClient(self.configuration))
        except BaseException:
            logger_settings.logger.info('There is some generic problem parsing the config file')