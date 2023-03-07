from kubernetes import client
from kubernetes.client.rest import ApiException
from InitData import InitData
from helpers import config_parser as parser
import os


class IngressManagementCreate(InitData):
    def __init__(self, auth_dict, service_name, service_port, path, rewrite=None, tls=None):
        super(IngressManagementCreate, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        :param service_name
        :param service_port
        :param path
        :host
        '''

        self.backend = client.NetworkingV1beta1IngressBackend(
            service_name=service_name,
            service_port=int(service_port)
        )

        self.paths = client.NetworkingV1beta1HTTPIngressPath(
            backend=self.backend,
            path=path)

        self.http = client.NetworkingV1beta1HTTPIngressRuleValue(paths=[self.paths])

        # get ingress host name from env var if is set
        hosts = os.environ.get('ingress_host', parser.config_params('ingress')['hosts'])
        # get tls secret name from env var if is set
        secret_name = os.environ.get('ingress_secret_name', parser.config_params('ingress')['secret_name'])

        # set rewrite target
        if rewrite:
            self.rewrite = rewrite
        else:
            # by default set to /
            self.rewrite = '/'

        # set tls
        if tls:
            self.tls = client.NetworkingV1beta1IngressTLS(hosts=[hosts], secret_name=secret_name)
            self.rule = client.NetworkingV1beta1IngressRule(host=hosts, http=self.http)
        else:
            self.tls = {}
            self.rule = client.NetworkingV1beta1IngressRule(http=self.http)

        self.spec = client.NetworkingV1beta1IngressSpec(rules=[self.rule], tls=[self.tls])

    def create_ingress_object(self, ingress_nane):
        '''
        :param ingress_nane:
        :param rewrite
        :return:
        '''

        ingress = client.ExtensionsV1beta1Ingress(
            api_version='extensions/v1beta1',
            kind='Ingress',
            # TODO we might want to add also annotation in objectmeta
            # EG: annotations={"kubernetes.io/ingress.class": "lot"}
            metadata=client.V1ObjectMeta(name=ingress_nane,
                                         annotations={'kubernetes.io/ingress.class': 'nginx',
                                                      'nginx.ingress.kubernetes.io/rewrite-target': self.rewrite}),
            spec=self.spec)
        return ingress

    def create_ingress(self, ingress, namespace):
        '''
        Create ingress
        :param ingress:
        :param namespace:
        :return:
        '''
        try:
            api_response = self.netwpork.create_namespaced_ingress(
                namespace=namespace,
                body=ingress)
            dat = api_response
        except ApiException as e:
            dat = 'Issue:{0} creating ingress:{1}'.format(e, ingress)
        return dat


class IngressManagementDelete(InitData):
    def __init__(self, auth_dict):
        super(IngressManagementDelete, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def delete_ingress(self, ingress_name, namespace=None):
        '''

        :param ingress_name:
        :param namespace:
        :return:
        '''
        try:
            # if namespace is not try to use the default namespace
            if namespace is None:
                namespace = 'default'

            api_response = self.netwpork.delete_namespaced_ingress(name=ingress_name, namespace=namespace,
                                                                       body=client.V1DeleteOptions(
                                                                           propagation_policy='Foreground',
                                                                           grace_period_seconds=5))
            dat = api_response
        except ApiException as e:
            dat = 'Issue:{0} deleting ingress:{1}'.format(e, ingress_name)
        return dat
