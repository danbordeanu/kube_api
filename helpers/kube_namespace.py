from kubernetes import client
from kubernetes.client.rest import ApiException
from InitData import InitData
from helpers import config_parser as parser
import os


class NameSpaceManagement(InitData):
    def __init__(self, auth_dict):
        super(NameSpaceManagement, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def namespace_create(self, namespace_name, owner=None, patch=False):
        '''
        create namespace
        :param auth_dict:
        :param namespace_name:
        :param owner
        :param patch
        :return:
        '''
        # set owner label to none
        # TODO maybe fetch user's team from ldap info somehow?
        # TODO remove this if, owner must be not None
        if owner is None:
            owner = 'noowner'
        body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace_name, labels={'owner': owner}))
        try:
            self.v1.create_namespace(body)
            dat = 'Namespace {0} created'.format(namespace_name)
        except ApiException as e:
            if e.status == 409 and patch:
                try:
                    api_response = self.v1.patch_namespace(name=namespace_name, body=body)
                    dat = str(api_response)
                except ApiException as e:
                    dat = 'issue:{0} patching namespace:{1}'.format(e, namespace_name)
            else:
                dat = 'Issue:{0} creating the namespace:{1}'.format(e, namespace_name)
        return dat

    def namespace_quota(self, namespace_name):
        '''
        allocate default quota to the new namespace
        :param namespace_name:
        :return:
        '''

        # https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/cpu-default-namespace/

        name_quota = parser.config_params('namespace')['name_quota']
        requests_cpu = os.getenv('NAMESPACE_REQUESTS_CPU', parser.config_params('namespace')['requests_cpu'])
        requests_memory = os.getenv('NAMESPACE_REQUESTS_MEMORY', parser.config_params('namespace')['requests_memory'])
        limits_cpu = os.getenv('NAMESPACE_LIMITS_CPU', parser.config_params('namespace')['limits_cpu'])
        limits_memory = os.getenv('NAMESPACE_LIMITS_MEMORY', parser.config_params('namespace')['limits_memory'])
        requests_storage = os.getenv('NAMESPACE_REQUESTS_STORAGE',
                                     parser.config_params('namespace')['requests_storage'])
        services_nodeports = os.getenv('NAMESPACE_SERVICE_NODEPORTS',
                                       parser.config_params('namespace')['services_nodeports'])
        replace = True

        resource_quota = client.V1ResourceQuota(metadata=client.V1ObjectMeta(namespace=namespace_name, name=name_quota),
                                                spec=client.V1ResourceQuotaSpec(
                                                    hard={'requests.cpu': requests_cpu,
                                                          'requests.memory': requests_memory, 'limits.cpu': limits_cpu,
                                                          'limits.memory': limits_memory,
                                                          'requests.storage': requests_storage,
                                                          'services.nodeports': services_nodeports}))

        try:
            if self.v1.list_namespaced_resource_quota(namespace_name).items:
                if not replace:
                    return
                    # updating quota
                return self.v1.replace_namespaced_resource_quota(name=name_quota, namespace=namespace_name,
                                                                 body=resource_quota)
            else:
                self.v1.create_namespaced_resource_quota(namespace_name, resource_quota)
                dat = 'Quota assigned for namespace:{0}'.format(namespace_name)
        except ApiException as e:
            dat = 'Issue:{0} allocating quota for namespace:{1}'.format(e, namespace_name)
        return dat

    def namespace_limits_ng_exp(self, namespace_name):
        '''
        :param namespace_name:
        :return:
        '''
        name_limits = parser.config_params('namespace')['name_limits']
        default_request_cpu = parser.config_params('namespace')['default_request_cpu']
        default_request_memory = parser.config_params('namespace')['default_request_memory']
        default_limit_cpu = parser.config_params('namespace')['default_limit_cpu']
        default_limit_memory = parser.config_params('namespace')['default_limit_memory']
        min_cpu = parser.config_params('namespace')['min_cpu']
        min_memory = parser.config_params('namespace')['min_memory']
        replace = True

        limit_range = client.V1LimitRange(
            metadata=client.V1ObjectMeta(name=name_limits, namespace=namespace_name),
            spec=client.V1LimitRangeSpec(limits=[client.V1LimitRangeItem(
                default={'cpu': default_limit_cpu, 'memory': default_limit_memory},
                default_request={'cpu': default_request_cpu, 'memory': default_request_memory},
                min={'cpu': min_cpu, 'memory': min_memory},
                type='Container'
            )])
        )

        try:
            if self.v1.list_namespaced_limit_range(namespace_name).items:
                if not replace:
                    return
                # updating the limit range
                return self.v1.replace_namespaced_limit_range(name=name_limits, namespace=namespace_name,
                                                              body=limit_range)
            else:
                self.v1.create_namespaced_limit_range(namespace=namespace_name, body=limit_range)
                dat = 'Limits assigned for namespace:{0}'.format(namespace_name)
        except ApiException as e:
            dat = 'Issue:{0} allocating limits for the namespace:{1}'.format(e, namespace_name)
        return dat

    def namespace_delete(self, namespace_name):
        '''
        delete namespace
        :param namespace_name:
        :return:
        '''
        try:
            self.v1.delete_namespace(name=namespace_name, body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
            dat = 'Namespace {0} deleted'.format(namespace_name)
        except ApiException as e:
            dat = 'Issue:{0} deleting the name space:{1}'.format(e, namespace_name)
        return dat
