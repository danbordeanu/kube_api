from helpers import config_parser as parser
from helpers import logger_settings
import os


class KubeAuthString(object):
    '''
    this will read the auth certs for the kubecluster, it will return a nice dictionary
    '''

    def __init__(self):
        # host value

        self.host = os.environ.get('host', parser.config_params('kubeauth')['host'])
        # check if certificate exists
        try:
            # certificate - authority - data
            self.ssl_ca_cert_file = os.environ.get('ssl_ca_cert_file', parser.config_params('kubeauth')['ssl_ca_cert_file'])
        except IOError as e:
            logger_settings.logger.error(' certificate-authority-data file missing:{0}'.format(e))

        try:
            # client - certificate - data
            self.ssl_cert_file = os.environ.get('ssl_cert_file', parser.config_params('kubeauth')['ssl_cert_file'])
        except IOError as e:
            logger_settings.logger.error('client-certificate-data file missing:{0}'.format(e))

        try:
            # client - key - data
            self.ssl_key_file = os.environ.get('ssl_key_file', parser.config_params('kubeauth')['ssl_key_file'])
        except IOError as e:
            logger_settings.logger.error('client-key-data file missing:{0}'.format(e))


        # proxy settings
        self.proxy = parser.config_params('kubeauth')['proxy']
        # context
        self.context = os.environ.get('context', parser.config_params('kubeauth')['context'])

    def give_me_auth_values(self):
        '''
        dict returned will be use by kube Configuration class
        :return:
        '''
        my_auth_dict = dict(host=self.host, ssl_ca_cert_file=self.ssl_ca_cert_file,
                            ssl_cert_file=self.ssl_cert_file, ssl_key_file=self.ssl_key_file, proxy=self.proxy,
                            context=self.context)
        return my_auth_dict
