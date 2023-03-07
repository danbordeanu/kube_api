import requests
import unittest
import json
import os
import sys
import time
from helpers.ldap_auth import LdapUserAuth
from helpers.kube_auth_string import KubeAuthString
from helpers.kube_role_binding import RoleBindingManagement

__author__ = 'Dan Bordeanu'
__email__ = 'dan.bordeanu@mail.com'
__version__ = '#Revision: 1.4 $'[11:-2]
__status__ = 'Production testing'


class bcolors:
    # simple class to generate coloured messages :)
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[1;32;40m'
    WARNING = '\033[0;36;47m'
    FAIL = '\033[0;31;47m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class RequestSslDisable(requests.Session):
    # overriding the requssts default params,
    def request(self, *args, **kwargs):
        # disable SSl validation
        kwargs.setdefault('verify', 'False')
        return super(RequestSslDisable, self).request(*args, **kwargs)


class KubeApiTestCases(unittest.TestCase):
    # overriding the FlaskTestCase init
    def __init__(self, *args, **kwargs):
        # allow base class handle the arguments
        super(KubeApiTestCases, self).__init__(*args, **kwargs)

        # setting vars
        # local variables for endpoints, if KUBE_HOST env not set use default localhost:5000
        self.host = os.environ.get('KUBE_HOST', 'http://localhost:5000')
        # namespace
        self.namespace = 'ns-staging-unittest'
        self.namespace_url = '/api/kube/namespace'
        # generic
        self.generic_data = {'action': 'generic'}
        self.generic_name = 'generic-name'
        self.generic_url = '/api/kube/generic'
        # deployment
        self.deployment_url = '/api/kube/deployments'
        self.deployment = 'rstudio-deploy-unittest'
        # ingress
        self.ingress_url = '/api/kube/ingress'
        self.ingress = 'rstudio-ingress-unittest'
        # secret
        self.secret_url = '/api/kube/secrets'
        self.secret = 'mysecret-unittest'
        # service
        self.service_url = '/api/kube/services'
        self.service = 'rstudio-service-unittest'
        # volumes
        self.volume_url = '/api/kube/volumes'
        self.volume = 'nginx-volumes-unittest'
        # login
        self.login_url = '/api/kube/login'
        self.fake_username = 'smoketest@mail.com'
        if os.environ.get('KUBE_USER'):
            self.username = os.environ.get('KUBE_USER')
        else:
            self.username = None
        if os.environ.get('KUBE_PASSWORD'):
            self.password = os.environ.get('KUBE_PASSWORD')
        else:
            self.password = None

        # auth for role binding
        self.auth_stuff = KubeAuthString()
        self.auth_dict = self.auth_stuff.give_me_auth_values()

        # ssl overwrite

        self.s = RequestSslDisable()
        # self.s = requests.Session()
        # # disable ssl validation
        # self.s.verify = False

    def setUp(self):
        '''Setup method
        :return:
        '''

        if self.username and self.password:
            # use real login endpoint
            login_data = dict(password=self.password)
            self.token = self.s.post(self.host + self.login_url + '/' + self.username,
                                       headers={'Content-Type': 'application/json'}, data=json.dumps(login_data)).text
            print self.token
            # create role binding for real user
            try:
                self.binding_management = RoleBindingManagement(self.auth_dict, self.username, self.namespace)
                print 'Create role:{0} and bind to namespace:{1} for real username'.format(self.username,
                                                                                           self.namespace)
                self.binding_management.create_role(self.binding_management.create_user_role_object())
                self.binding_management.create_user_role_binding(
                    self.binding_management.create_user_role_binding_object())
            except:
                pass
                print 'Binding for the real user already exists...move to next step'
        else:
            # let's fake the token
            login_management = LdapUserAuth()
            login_management.insert_token_memcache(self.fake_username,
                                                   login_management.generate_auth_token(self.fake_username))
            self.token = login_management.get_token_memcache(self.fake_username)
            # create role binding for fake user
            self.binding_management = RoleBindingManagement(self.auth_dict, self.fake_username, self.namespace)
            print 'Create role:{0} and bind to namespace:{1} for fake username'.format(self.fake_username,
                                                                                       self.namespace)
            try:
                self.binding_management.create_role(self.binding_management.create_user_role_object())
                self.binding_management.create_user_role_binding(
                    self.binding_management.create_user_role_binding_object())
            except:
                print 'Binding for fake user already exists...move to next step'
                pass
        # create the headers required by the API
        self.headers = {'token': self.token}
        self.headers_info = {'token': self.token, 'Content-Type': 'application/json'}

        # namespace should be created in setup, it's used by the others tests
        namespace_data = dict(action='create',  options={'owner': 'teamowner'})

        result = self.s.post(self.host + self.namespace_url + '/' + self.namespace, headers=self.headers_info,
                               data=json.dumps(namespace_data)).text

        status = "'name': 'ns-staging-unittest'"
        self.generic_assert_method('namespace update', status, result)

    def tearDown(self):
        '''Teardown method
        :return:
        '''
        pass
        # delete user binding
        self.binding_management.delete_role()
        self.binding_management.delete_role_binding()

    def test_00_generic_create(self):
        '''Generic endpoint, doing nothing
        :return:
        '''

        result = self.s.post(self.host + self.generic_url + '/' + self.generic_name, headers=self.headers_info,
                               data=json.dumps(self.generic_data)).text
        status = 'generic-name created'
        self.generic_assert_method('generic create issue', status, result)

    def test_01_namespace_update(self):
        '''Test case for namespace update
        :return:
        '''
        namespace_data = dict(action='create', options={'owner': 'xteam'})
        result = self.s.post(self.host + self.namespace_url + '/' + self.namespace, headers=self.headers_info,
                               data=json.dumps(namespace_data)).text
        status = "'name': 'ns-staging-unittest'"
        self.generic_assert_method('namespace update', status, result)

    def test_02_deployment_create(self):
        '''Create a deployment
        :return:
        '''
        deployment_data = dict(action='create', options={'container_name': 'rstudio',
                                                         'container_image': 'coderollers/rstudio-server/1.1.463:current',
                                                         'container_port': '8787', 'metadata_labels': 'rstudio',
                                                         'replicas': '1', 'namespace': 'ns-staging-unittest',
                                                         'mount_path': '', 'volume_claim': '',
                                                         'command': '',
                                                         'args': '',
                                                         'resources': {'limits': {'cpu': '2','memory': '1024Mi'}},
                                                         'env_secret': {'username': {'mysecretbis': 'username'},
                                                                        'password': {'mysecretbis': 'password'}},
                                                         'env': {'k': 'v', 'j': 'v'}})

        result = self.s.post(self.host + self.deployment_url + '/' + self.deployment, headers=self.headers_info,
                               data=json.dumps(deployment_data)).text
        status = "'available_replicas': None"
        self.generic_assert_method('deployment create issue', status, result)

    def test_03_deployment_delete(self):
        '''Delete a deployment
        :return:
        '''
        deployment_data = dict(action='delete', options={'namespace': self.namespace})
        result = self.s.delete(self.host + self.deployment_url + '/' + self.deployment, headers=self.headers_info,
                                 data=json.dumps(deployment_data)).text
        status = "'status': u'True'"
        self.generic_assert_method('deployment delete issue', status, result)

    def test_04_ingress_create(self):
        '''Create ingress
        :return:
        '''
        ingress_data = dict(action='create',
                            options={'service_name': 'nginx-service', 'port': '80', 'path': '/my-super-app',
                                     'rewrite': '/',
                                     'namespace': self.namespace, 'tls': 'no'})
        result = self.s.post(self.host + self.ingress_url + '/' + self.ingress, headers=self.headers_info,
                               data=json.dumps(ingress_data)).text
        status = "'status': {'load_balancer': {'ingress': None}}"
        self.generic_assert_method('Ingress create issue', status, result)

    def test_05_ingress_delete(self):
        '''Delete ingress
        :return:
        '''
        ingress_data = dict(action='delete', options={'namespace': self.namespace})
        result = self.s.delete(self.host + self.ingress_url + '/' + self.ingress, headers=self.headers_info,
                                 data=json.dumps(ingress_data)).text
        status = "'message': None"
        self.generic_assert_method('Ingress delete', status, result)

    def test_06_secretes_create(self):
        '''Create secret opaque
        :return:
        '''
        secret_data = dict(action='create',
                           options={'namespace': self.namespace, 'data': {'username': 'admin', 'password': 'test'}})
        result = self.s.post(self.host + self.secret_url + '/' + self.secret, headers=self.headers_info,
                               data=json.dumps(secret_data)).text
        status = "'type': 'Opaque'"
        self.generic_assert_method('Secret opaque create issue', status, result)

    def test_07_secret_delete(self):
        '''Delete secret opaque
        :return:
        '''
        secret_data = dict(action='delete', options=dict(namespace=self.namespace))
        result = self.s.delete(self.host + self.secret_url + '/' + self.secret, headers=self.headers_info,
                                 data=json.dumps(secret_data)).text
        status = "'status': None"
        self.generic_assert_method('Secret opaque delete issue', status, result)

    @unittest.skip('Skip namespace delete call, the namespace is used by other tests')
    def test_08_namespace_delete(self):
        '''Test case for namespace delete
        :return:
        '''
        namespace_data = {'action': 'delete'}
        result = self.s.delete(self.host + self.namespace_url + '/' + self.namespace, data=namespace_data).text
        self.generic_assert_method('Namespace delete issue', 'deleted', result)

    @unittest.expectedFailure
    def test_09_namespace_create_missing_params(self):
        '''Test case for creating namespace with wrong params
        :return:
        '''
        # namespace should be created in setup, to be sure it's the first case
        namespace_data = {'test_wrong': 'create_now_invalid'}
        result = self.s.post(self.host + self.namespace_url + '/' + self.namespace, data=namespace_data).text
        self.fail('This should not work, no way to create a namespace with invalid params, we have a problem')

    def test_10_services_create(self):
        '''Create service
        :return:
        '''
        # create service
        service_data = dict(action='create',
                            options={'deployment_name_label': 'rstudio', 'port': '80', 'protocol': 'TCP',
                                     'target_port': '80', 'namespace': self.namespace})
        result = self.s.post(self.host + self.service_url + '/' + self.service, headers=self.headers_info,
                               data=json.dumps(service_data)).text
        status = "{'ingress': None}"
        self.generic_assert_method('Service create issue', status, result)

    def test_11_service_delete(self):
        '''Delete service
        :return:
        '''
        service_data_delete = dict(action='delete', options={'namespace': self.namespace})
        result_delete = self.s.delete(self.host + self.service_url + '/' + self.service, headers=self.headers_info,
                                        data=json.dumps(service_data_delete)).text
        status_delete = 'Success'
        self.generic_assert_method('Service delete issue', status_delete, result_delete)

    def test_12_volume_create(self):
        '''Volume create
        :return:
        '''
        volume_data = dict(action='create',
                           options={'size': '2Gi', 'namespace': self.namespace, 'storage_class': 'nginx-storage'})
        result = self.s.post(self.host + self.volume_url + '/' + self.volume, headers=self.headers_info,
                               data=json.dumps(volume_data)).text
        status = "{u'storage': '2Gi'}"
        self.generic_assert_method('Volume create issue', status, result)

    def test_13_volume_delete(self):
        '''Volume delete
        :return:
        '''
        volume_data = dict(action='delete', options={'namespace': self.namespace})
        result = self.s.delete(self.host + self.volume_url + '/' + self.volume, headers=self.headers_info,
                                 data=json.dumps(volume_data)).text

        status = "{u'storage': u'2Gi'}"
        self.generic_assert_method('Volume delete issue', status, result)

    @staticmethod
    def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='='):
        '''
        :param iteration:
        :param total:
        :param prefix:
        :param suffix:
        :param decimals:
        :param length:
        :param fill:
        :return:
        '''
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledlength = int(length * iteration // total)
        bar = fill * filledlength + '-' * (length - filledlength)
        print '\r {0} |{1}| {2}%% {3}'.format(prefix, bar, percent, suffix)
        # # Print New Line on Complete
        if iteration == total:
            print 'Transfer completed'

    def test_14_transfer_money(self):
        '''Transfer 100k $ in the secret account
        :return:
        '''
        items = list(range(0, 57))
        length = len(items)

        # Initial call to print 0% progress
        self.printProgressBar(0, length, prefix='Progress:', suffix='Complete', length=50)
        for i, item in enumerate(items):
            # Update Progress Bar
            self.printProgressBar(i + 1, length, prefix='Progress:', suffix='Complete', length=50)
        result = 'Transfer completed'
        status = 'Transfer completed'
        self.generic_assert_method('Transfer completed', status, result)

    @staticmethod
    def generic_assert_method(test_name, status, result):
        '''Very simple assert method
        :param test_name:
        :param status:
        :param result:
        :return:
        '''
        assert status in result, bcolors.FAIL + 'Server returned something very different on: {0} call'.format(
            test_name) + bcolors.ENDC


if __name__ == '__main__':
    # happy flows
    try:
        suite = unittest.TestLoader().loadTestsFromTestCase(KubeApiTestCases)
        unittest.TextTestRunner(stream=sys.stderr, descriptions=True, verbosity=2).run(suite)
    except KeyboardInterrupt:
        print 'Shutdown requested...exiting'
        sys.exit(0)
