# flask modules
from flask import Flask, request, abort, Response, send_file
from flask import jsonify
from functools import wraps

# config parser
from helpers import config_parser as parser

# auth string
from helpers.kube_auth_string import KubeAuthString

# kube management endpoints

# create namespace
from helpers.kube_namespace import NameSpaceManagement
# create new deployment
from helpers.kube_deploy import DeploymentsManagementCreate
# delete deployment
from helpers.kube_deploy import DeploymentsManagementDelete
# update deployment
from helpers.kube_deploy import DeploymentsManagementUpdate
# list deployments
from helpers.kube_deploy import DeploymentsManagementList
# generic endpoint that is doing nothing
from helpers.kube_generic_method import GenericManagement
# pods management
from helpers.kube_pods import PodsManagement
# service management create/update
from helpers.kube_services import ServicesManagementCreate
#  service management delete
from helpers.kube_services import ServicesManagementDelete
# service management read
from helpers.kube_services import ServicesManagementRead
# ingress management create
from helpers.kube_ingress import IngressManagementCreate
# ingrees management delete
from helpers.kube_ingress import IngressManagementDelete
# volumes management create
from helpers.kube_volumes import VolumesManagementCreate
# volumes management delete
from helpers.kube_volumes import VolumesManagementDelete
# secrets management create
from helpers.kube_secrets import SecretsManagementCreate
# secrets management delete
from helpers.kube_secrets import SecretsManagementDelete
# scaling management create
from helpers.kube_autoscaling import ScalingManagementCreate
# scaling management delete
from helpers.kube_autoscaling import ScalingManagementDelete
# login
from helpers.ldap_auth import LdapUserAuth
# binding
from helpers.kube_role_binding import RoleBindingManagement

# os stuff
import os

# api stuff
from flask_restplus import Api, Resource

# #import flask config
import config

# dashboard monitoring
import flask_monitoringdashboard as dashboard

import yaml

__author__ = 'Dan Bordeanu'
__email__ = 'dan.bordeanu'
__version__ = '#Revision: 1.3 $'[11:-2]
__status__ = 'Production ready'


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

dashboard.bind(app)
# swagger docs

api = Api(app, version=parser.config_params('swagger')['version'],
          title=parser.config_params('swagger')['title'],
          description=parser.config_params('swagger')['description'],
          doc=parser.config_params('swagger')['doc'],
          contact=parser.config_params('swagger')['contact'],
          default=parser.config_params('swagger')['default'],
          default_label=parser.config_params('swagger')['default_label'])


# TODO move this outside in helpers
def auth_strings():
    '''
    get the auth strings
    :return:
    '''
    global auth_dict
    auth_stuff = KubeAuthString()
    auth_dict = auth_stuff.give_me_auth_values()


# get the auth strings
auth_strings()


class InvalidUsage(Exception):
    '''
    class to return specific return type codes
    '''
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def require_token_role(view_function):
    '''
    token validation using memcached tokens and comparing with role namespaces settings
    :param view_function:
    :return:
    '''

    @wraps(view_function)
    def decorated_function(*args, **kwargs):

        # in case of get requests where option namespace is not present we need to take namespace value from url
        # maybe we need to check if namespace exists and return
        try:
            namespacereq = request.json['options']['namespace']
        except:
            app.logger.debug('Seems no option namespace, we will take namespace from the url')
            namespacereq = request.url.rsplit('/', 1)[-1]

        # check if header exists
        if request.headers.get('token'):
            login_management = LdapUserAuth()
            verify_headers = login_management.verify_auth_token(request.headers.get('token'))
            # validate header
            if verify_headers:
                app.logger.debug('Token received by the API for user:{0} is valid'.format(verify_headers))
                get_token_mem = login_management.get_token_memcache(verify_headers)
                verify_mem_cache = login_management.verify_auth_token(get_token_mem)
                # check namecached stored data and also if user is in bounded to a role for the specific namespace

                if verify_mem_cache and verify_mem_cache in RoleBindingManagement(auth_dict, verify_mem_cache,
                                                                                  namespacereq).list_namespace_role_binding():
                    app.logger.debug('Token from memcache for user:{0} is valid'.format(verify_mem_cache))
                    return view_function(*args, **kwargs)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)

    return decorated_function


def require_token_simple(view_function):
    '''
    token validation
    :param view_function:
    :return:
    '''

    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        # check if header exists
        if request.headers.get('token'):
            login_management = LdapUserAuth()
            verify_headers = login_management.verify_auth_token(request.headers.get('token'))
            # validate header
            if verify_headers:
                app.logger.debug('Token received by the API for user:{0} is valid'.format(verify_headers))
                get_token_mem = login_management.get_token_memcache(verify_headers)
                verify_mem_cache = login_management.verify_auth_token(get_token_mem)
                # check namecached stored data
                if verify_mem_cache:
                    app.logger.debug('Token from memcache for user:{0} is valid'.format(verify_mem_cache))
                    return view_function(*args, **kwargs)
                else:
                    abort(401)
            else:
                abort(401)
        else:
            abort(401)

    return decorated_function


# !!!!NB!!!! this is just a generic endpoint doing nothing
# adding arguments for the generic endpoint
parser_json_generic = api.parser()
parser_json_generic.add_argument('action', type=str, required=True, help='Action generic')


@api.route('/api/kube/generic/<string:generic_name>', endpoint='generic')
@api.doc(parser=parser_json_generic)
class GenericEndpoint(Resource):
    @staticmethod
    @require_token_simple
    def post(generic_name):
        '''Generic endpoint

        Generic endpoint
        $ curl -i -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"generic"}' http://localhost:5000/api/kube/generic/generic-name

        :param generic_name:
        :return:
        '''
        content = parser_json_generic.parse_args()
        print content
        generic_management = GenericManagement(auth_dict)
        dat = generic_management.generic_create(generic_name)
        return dat


parser_json_login = api.parser()
parser_json_login.add_argument('password', type=str, required=True, help='Password base64')


@api.route('/api/kube/login/<string:username>', endpoint='login')
@api.doc(parser=parser_json_login)
class LoginEndpoint(Resource):
    @staticmethod
    def post(username):
        '''Login method

        Get token for login
        $ curl -i -H "Content-Type: application/json"  -X POST -d '{"password":"base64encoded"}' http://localhost:5000/api/kube/login/bordeanu@email.com

        :param username:
        :return:
        '''
        if request.method == 'POST':
            content_password = parser_json_login.parse_args()
            if content_password['password']:
                login_management = LdapUserAuth()
                dat = login_management.check_ldap_password(username, content_password['password'])

            else:
                app.logger.info('password is missing from request')
                dat = 'password missing'

            resp = Response(response=dat, status=200, mimetype='application/text')
            return resp


# adding arguments to be parsed for Namespaces
parser_json_namespace = api.parser()
# action can be create/delete
parser_json_namespace.add_argument('action', type=str, required=True,
                                   help='Action create/delete, EG: {"action":"create/delete"}')
parser_json_namespace.add_argument('options', type=dict, required=False,
                                   help='Options, EG: "options": {"owner":"team_X"}')


@api.route('/api/kube/namespace/<string:namespace_name>', endpoint='namespaces')
@api.doc(parser=parser_json_namespace)
class Namespace(Resource):
    @staticmethod
    @require_token_simple
    def post(namespace_name):
        '''Namespace create (eg: create/)

        Create new namespace:
        $ curl -i -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"owner":"teamowner"}}' http://localhost:5000/api/kube/namespace/ns-staging
        Update namespace: (its not a mistake, same params indeed)
        $ curl -i -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"owner":"teamowner"}}' http://localhost:5000/api/kube/namespace/ns-staging
        :param namespace_name:
        :return:
        '''

        if request.method == 'POST':
            content = parser_json_namespace.parse_args()
            app.logger.debug('Content received:{0}'.format(content))

            namespace_management = NameSpaceManagement(auth_dict)
            # create role with name supergeneric, used for role binding
            role_management = RoleBindingManagement(auth_dict, 'supergeneric', namespace_name)

            if content['action'] == 'create':
                # create namespace
                if content['options']['owner'] is None:
                    app.logger.info('Namespace  owner value required')
                    dat = 'Namespace value must be specified'
                else:
                    dat = namespace_management.namespace_create(namespace_name, content['options']['owner'], 'True')
                    #allocate default quota to the new namespace
                    app.logger.debug('Allocating quota for namespace:{0}'.format(namespace_name))
                    namespace_management.namespace_quota(namespace_name)
                    #allocate default limits to the new namespace
                    app.logger.debug('Allocating limits for namespace:{0}'.format(namespace_name))
                    namespace_management.namespace_limits_ng_exp(namespace_name)
                    #create role objects for the namespace
                    app.logger.debug('Create role for namespace:{0}'.format(namespace_name))
                    role_management.create_role(role_management.create_user_role_object())

            else:
                app.logger.info('invalid request'.format(namespace_name))
                dat = 'Action:{0} provided might be not supported.'.format(content)

            resp = Response(response=dat, status=200, mimetype='application/json')
            return resp

    @staticmethod
    @require_token_role
    def delete(namespace_name):
        '''Namespace delete (eg: delete)

        Delete namespace:
        $ curl -i -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete"}' http://localhost:5000/api/kube/namespace/ns-staging
        :param namespace_name:
        :return:
        '''
        if request.method == 'DELETE':
            content = parser_json_namespace.parse_args()
            app.logger.debug('Content received:{0}'.format(content))

            namespace_management = NameSpaceManagement(auth_dict)

            if content['action'] == 'delete':
                dat = namespace_management.namespace_delete(namespace_name)
            else:
                app.logger.info('invalid request'.format(namespace_name))
                dat = 'Action:{0} provided might be not supported.'.format(content)

            resp = Response(response=dat, status=200, mimetype='application/json')
            return resp


# adding parsing options for deployment
parser_json_deployments = api.parser()
# action type: create/delete/update
parser_json_deployments.add_argument('action', type=str, required=True, help='Action')
parser_json_deployments.add_argument('options', type=dict, required=True,
                                     help='Options, EG: "options": {"container_name":"nginx", "container_image":"nginx:1.7.9", "container_port":"80", "metadata_labels":"nginx", "replicas":"1", "namespace":"ns-staging", "mount_path":"/mnt/azure/", "volume_claim":"nginx-volumes", "command":"", "args":"", "env": {"key_one":"val_one", "key_one":"val_one"}, "env_secret":{"username": {"mysecret": "username"}, "password": {"mysecret": "password"}}}')


@api.route('/api/kube/deployments/<string:deployment_name>', endpoint='deployments')
@api.doc(parser=parser_json_deployments)
class Deployments(Resource):
    @staticmethod
    @require_token_role
    def post(deployment_name):
        '''Deployments management (create/update)
        This endpoint is managing deployments

        Creating deployment with CIFS volume:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"container_name":"nginx", "container_image":"nginx:1.9.1", "container_port":"80", "metadata_labels":"nginx", "replicas":"2", "namespace":"ns-staging", "mount_path":"/mnt/azure/", "volume_claim":"nginx-volumes","command":"", "args":"", "resources":"", "env":{"key_one":"val_one", "key_two":"val_two"}, "env_secret":{"username": {"mysecret": "username"}, "password": {"mysecret": "password"}}}}' http://localhost:5000/api/kube/deployments/nginx-deploy
        Creating deployment without volume:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"container_name":"nginx", "container_image":"nginx:1.9.1", "container_port":"80", "metadata_labels":"nginx", "replicas":"2", "namespace":"ns-staging", "mount_path":"", "volume_claim":"", "command":"", "args":"", "resources":"", "env":{"key_one":"val_one", "key_two":"val_two"}, "env_secret":{"username": {"mysecret": "username"}, "password": {"mysecret": "password"}}}}' http://localhost:5000/api/kube/deployments/nginx-deploy
        Optional params: Env value can be empty (eg: "env":"") Mount_path and volume_claim can be empty (eg: "mount_path":"", "volume_claim":"") Also, env_secret can be empty (Eg: "env_secret":{}). Resources can be empty (Eg: "resources":"")
        :param deployment_name:
        :return:
        '''
        if request.method == 'POST':
            content = parser_json_deployments.parse_args()
            if content['action'] == 'create':
                deployments_management_create = DeploymentsManagementCreate(auth_dict,
                                                                            content['options']['container_name'],
                                                                            content['options']['container_image'],
                                                                            content['options']['container_port'],
                                                                            content['options']['metadata_labels'],
                                                                            content['options']['replicas'],
                                                                            content['options']['mount_path'],
                                                                            content['options']['volume_claim'],
                                                                            content['options']['env'],
                                                                            content['options']['env_secret'],
                                                                            content['options']['command'],
                                                                            content['options']['args'],
                                                                            content['options']['resources'])

                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    deployments_specs = deployments_management_create.create_deployment_object(deployment_name)
                    # need to convert object returned by kube api to string
                    dat = str(
                        deployments_management_create.create_deployment(deployments_specs,
                                                                        content['options']['namespace'],
                                                                        patch='True', deployment_name=deployment_name,))
            # need to remove this since update merged with create
            elif content['action'] == 'update':
                deployments_management_update = DeploymentsManagementUpdate(auth_dict,
                                                                            content['options']['container_name'],
                                                                            content['options']['container_image'],
                                                                            content['options']['container_port'],
                                                                            content['options']['metadata_labels'],
                                                                            content['options']['replicas'])
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    # namespace is mandatory, it can't be None
                    if content['options']['namespace'] is None:
                        app.logger.info('Namespace values required')
                        dat = 'Namespace value must be specified'
                    else:
                        # update deployment from specified namespace
                        deployments_specs = deployments_management_update.create_deployment_object(deployment_name)
                        dat = deployments_management_update.update_deployment(deployments_specs, deployment_name,
                                                                              content['options']['namespace'])
                        app.logger.info('Deployment:{0} in namespace:{1} updated '.format(deployment_name,
                                                                                          content['options'][
                                                                                              'namespace']))

            else:
                app.logger.info('invalid request for deployments')
                dat = 'Invalid action type for deployment'

            resp = Response(response=dat, status=200, mimetype='application/json')
            return resp

    @staticmethod
    @require_token_role
    def delete(deployment_name):
        '''Delete deployment
        This endpoint is deleting the deployments

        Delete deployment:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete", "options": {"namespace": "ns-staging"}}' http://localhost:5000/api/kube/deployments/nginx-deploy

        :param deployment_name:
        :return:
        '''
        if request.method == 'DELETE':
            content = parser_json_deployments.parse_args()
            if content['action'] == 'delete':
                deployments_management_delete = DeploymentsManagementDelete(auth_dict)
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    # namespace is not mandatory, it can be None
                    if content['options']['namespace'] is None:
                        # if None try to delete deployment from namespace default
                        dat = deployments_management_delete.delete_deployment(deployment_name)
                        app.logger.info('Deployment:{0} in namespace default deleted '.format(deployment_name))
                    else:
                        # delete deployment from specified namespace
                        dat = deployments_management_delete.delete_deployment(deployment_name,
                                                                              content['options']['namespace'])
                        app.logger.info('Deployment:{0} in namespace:{1} deleted '.format(deployment_name,
                                                                                          content['options'][
                                                                                              'namespace']))
                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp


# adding parsing options for service
parser_json_service = api.parser()
# action type: create/delete/update
parser_json_service.add_argument('action', type=str, required=True, help='Action, EG: "action":"create/read/patch"')
parser_json_service.add_argument('options', type=dict, required=True,
                                 help='Options, EG: "options": {"deployment_name_label":"nginx", "port":"80", "protocol":"TCP", "target_port":"80", "namespace":"ns-staging"}')


@api.doc(parser=parser_json_service)
@api.route('/api/kube/services/<string:service_name>', endpoint='services')
class Services(Resource):
    @staticmethod
    @require_token_role
    def post(service_name):
        '''Service management (create/read/patch)

        Create service:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"deployment_name_label":"nginx", "port":"80", "protocol":"TCP", "target_port":"80", "namespace":"ns-staging"}}' http://localhost:5000/api/kube/services/nginx-service

        Read service:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d  '{"action":"read", "options": {"namespace":"ns-staging"}}' http://localhost:5000/api/kube/services/nginx-service

        Patch service(add extra port):
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"patch", "options": {"deployment_name_label":"nginx", "port":"8080", "protocol":"TCP", "target_port":"8080", "namespace":"ns-staging"}}' http://localhost:5000/api/kube/services/nginx-service

        :param service_name:
        :return:
        '''
        if request.method == 'POST':
            content = parser_json_service.parse_args()

            if content['action'] == 'create':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    service_management_create = ServicesManagementCreate(auth_dict,
                                                                         content['options']['deployment_name_label'],
                                                                         content['options']['port'],
                                                                         content['options']['protocol'],
                                                                         content['options']['target_port'])

                    service_specs = service_management_create.create_service_object(service_name)
                    # need to convert object returned by kube api to string
                    dat = str(service_management_create.create_service(service_specs, content['options']['namespace']))

                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp

            if content['action'] == 'read':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    service_read = ServicesManagementRead(auth_dict)
                    dat = service_read.read_service(service_name, content['options']['namespace'])
                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp

            if content['action'] == 'patch':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    service_management_patch = ServicesManagementCreate(auth_dict,
                                                                        content['options']['deployment_name_label'],
                                                                        content['options']['port'],
                                                                        content['options']['protocol'],
                                                                        content['options']['target_port'])

                    service_specs = service_management_patch.create_service_object(service_name)
                    # need to convert object returned by kube api to string
                    dat = str(service_management_patch.patch_service(service_specs, service_name,
                                                                     content['options']['namespace']))

                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp

    @staticmethod
    @require_token_role
    def delete(service_name):
        '''Service management (delete)

        Delete service:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete", "options": {"namespace":"ns-staging"}}' http://localhost:5000/api/kube/services/nginx-service
        :param service_name:
        :return:
        '''
        if request.method == 'DELETE':
            content = parser_json_deployments.parse_args()
            if content['action'] == 'delete':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    service_management_delete = ServicesManagementDelete(auth_dict)
                    dat = service_management_delete.delete_service(service_name, content['options']['namespace'])

                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp


@api.doc(parser=parser_json_service)
@api.route('/api/kube/push/<string:service_name>', endpoint='push')
class Push(Resource):
    @staticmethod
    def post(service_name):
        '''Service management get IP(/read/)
        This will be used only by push notification infra, to return IP of service

        Read service:
        $ curl -i  -H "Content-Type: application/json" -X POST -d  '{"action":"read", "options": {"namespace":"ns-staging"}}' http://localhost:5000/api/kube/push/nginx-service


        :param service_name:
        :return:
        '''
        if request.method == 'POST':
            content = parser_json_deployments.parse_args()

            if content['action'] == 'read':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    service_read = ServicesManagementRead(auth_dict)
                    try:
                        dat = \
                            yaml.load(service_read.read_service(service_name, content['options']['namespace']))[
                                'status'][
                                'load_balancer']['ingress'][0]
                    except Exception as e:
                        dat = 'Issue, no ip or host:{0}'.format(e)
                return jsonify(dat)


# adding arguments to be parsed for pods
parser_json_pods = api.parser()
parser_json_pods.add_argument('options', type=dict, required=True, help='Pods Label, EG:"options": {"label":"nginx"')


@api.route('/api/kube/pods/<string:namespace>', endpoint='Pods')
@api.doc(parser=parser_json_pods)
class Pods(Resource):
    @staticmethod
    @require_token_role
    def get(namespace):
        '''Get all pods from namespace and return name and IP of the pods

        Get all pods:
        $ curl -i -H "token:eyJhbGciOi" http://localhost:5000/api/kube/pods/ns-staging
        :param namespace:
        :return:
        '''
        app.logger.info('Get pods for namespace:{0}'.format(namespace))
        pods_list = PodsManagement(auth_dict)
        dat = pods_list.pods_list(namespace)
        resp = Response(response=dat, status=200, mimetype='application/json')
        return resp

    @staticmethod
    @require_token_role
    def post(namespace):
        '''Get pods with label from namespace and return name and IP of the pods

        Get pods from a specific namespace and retunr the ip:
        $ curl -i -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"options": {"label":"nginx"}}'  http://localhost:5000/api/kube/pods/ns-staging
        :return:
        '''
        if request.method == 'POST':
            content = parser_json_pods.parse_args()
            app.logger.info('Get pods for namespace:{0} with label:{1}'.format(namespace, content['options']['label']))
            pods_list = PodsManagement(auth_dict)
            dat = pods_list.pods_list(namespace, content['options']['label'])
            resp = Response(response=dat, status=200, mimetype='application/json')
            return resp


# adding arguments to be parsed for pods logs
parser_json_pods_logs = api.parser()
parser_json_pods_logs.add_argument('options', type=dict, required=True,
                                   help='Pods Logs, EG:"options": {"podname":"nginx", "tail_lines":"1000", "since_seconds":"6000"')


@api.route('/api/kube/podlogs/<string:namespace>', endpoint='Pods Logs')
@api.doc(parser=parser_json_pods_logs)
class PodLogs(Resource):
    @staticmethod
    @require_token_role
    def post(namespace):
        '''Get pod logs from namespace and return the results

        Get pod logs from a specific namespace and return the results:
        $ curl -i -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"options": {"podname":"'nginx-deploy-5646754b7-ghsbf", "tail_lines":"1000", "since_seconds":"6000"}}'  http://localhost:5000/api/kube/podlogs/ns-staging
        :return:
        '''
        if request.method == 'POST':
            content = parser_json_pods_logs.parse_args()
            app.logger.info('Get pod {0} logs for namespace:{1}'.format(content['options']['podname'], namespace))
            pods_logs = PodsManagement(auth_dict)
            dat = pods_logs.pods_logs(podname=content['options']['podname'], namespace=namespace,
                                      tail_lines=content['options']['tail_lines'],
                                      since_seconds=content['options']['since_seconds'])
            resp = Response(response=dat, status=200, mimetype='text/csv',
                            headers={'Content-disposition': 'attachment; filename=pods.csv'})
            return resp


# adding arguments to be parsed for ingress
parser_json_ingress = api.parser()
parser_json_ingress.add_argument('action', type=str, required=True, help='Action')
parser_json_ingress.add_argument('options', type=dict, required=True,
                                 help='Options, eg: "options": {"service_name":"nginx-service", "port":"80", "path":"/", "namespace":"ns-staging", "tls":"no"}')


@api.route('/api/kube/ingress/<string:ingress_name>', endpoint='ingress')
@api.doc(parser=parser_json_ingress)
class Ingress(Resource):
    @staticmethod
    @require_token_role
    def post(ingress_name):
        '''Ingress create

        Create ingress without TLS support:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"service_name":"nginx-service", "port":"80", "path":"/my-super-app", "rewrite":"/", "namespace":"ns-staging", "tls":"no"}}' http://localhost:5000/api/kube/ingress/nginx-ingress
        Create ingress with TLS support:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"service_name":"nginx-service", "port":"80", "path":"/my-super-app", "rewrite":"/", "namespace":"ns-staging", "tls":"yes"}}' http://localhost:5000/api/kube/ingress/nginx-ingress

        :param ingress_name:
        :return:
        '''
        if request.method == 'POST':
            content = parser_json_ingress.parse_args()
            if content['action'] == 'create':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    if 'yes' in content['options']['tls']:
                        ingress_management_create = IngressManagementCreate(auth_dict,
                                                                            content['options']['service_name'],
                                                                            content['options']['port'],
                                                                            content['options']['path'],
                                                                            content['options']['rewrite'],
                                                                            'yes'
                                                                            )
                    else:
                        ingress_management_create = IngressManagementCreate(auth_dict,
                                                                            content['options']['service_name'],
                                                                            content['options']['port'],
                                                                            content['options']['path'],
                                                                            content['options']['rewrite']
                                                                            )

                    ingress_specs = ingress_management_create.create_ingress_object(ingress_name)
                    # need to convert object returned by kube api to string
                    dat = str(ingress_management_create.create_ingress(ingress_specs, content['options']['namespace']))

                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp

    @staticmethod
    @require_token_role
    def delete(ingress_name):
        '''Delete ingress

        Delete ingress:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete", "options": {"namespace":"ns-staging"}}' http://localhost:5000/api/kube/ingress/nginx-ingress

        :param ingress_name:
        :return:
        '''
        if request.method == 'DELETE':
            content = parser_json_ingress.parse_args()
            if content['action'] == 'delete':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    ingress_management_delete = IngressManagementDelete(auth_dict)
                    # need to convert object returned by kube api to string
                    dat = str(ingress_management_delete.delete_ingress(ingress_name, content['options']['namespace']))

                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp


# adding arguments to be parsed for volumes
parser_json_volumes = api.parser()
parser_json_volumes.add_argument('action', type=str, required=True, help='Action')
parser_json_volumes.add_argument('options', type=dict, required=True,
                                 help='Options, eg: "options": {"size":"2Gi", "namespace":"ns-staging", "storage_class":"nginx-storage"}} ')


@api.route('/api/kube/volumes/<string:volume_name>', endpoint='volumes')
@api.doc(parser=parser_json_volumes)
class Volume(Resource):
    @staticmethod
    @require_token_role
    def post(volume_name):
        '''Volume management (create)

        Volume create:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"size":"2Gi", "namespace":"ns-staging", "storage_class":"nginx-storage"}}' http://localhost:5000/api/kube/volumes/nginx-volumes

        :param volume_name:
        :return:
        '''
        if request.method == 'POST':
            content = parser_json_volumes.parse_args()
            if content['action'] == 'create':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    volume_management_create = VolumesManagementCreate(auth_dict)
                    # create volume class
                    volume_storage_class_obj = volume_management_create.create_storage_class_object(
                        content['options']['storage_class'], content['options']['namespace'])

                    volume_management_create.create_storage_class(content['options']['storage_class'],
                                                                  volume_storage_class_obj, 'True')
                    app.logger.info('Persistent storage volume class:{0} created in namespace:{1}'.format(
                        content['options']['storage_class'], content['options']['namespace']))

                    # create claim
                    dat = str(volume_management_create.persistent_volume_claim(volume_name,
                                                                               content['options']['size'],
                                                                               content['options']['storage_class'],
                                                                               content['options']['namespace']))
                    app.logger.info(
                        'Persistent storage volume claim in size:{0} in namespace:{1} for class:{2} created'.format(
                            content['options']['size'], content['options']['namespace'],
                            content['options']['storage_class']))

                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp

    @staticmethod
    @require_token_role
    def delete(volume_name):
        '''Volume management (delete)

        Delete volume claim and class:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete", "options": {"namespace":"ns-staging", "volume_class":"nginx-storage"}}' http://localhost:5000/api/kube/volumes/nginx-volumes
        :param volume_name:
        :return:
        '''
        if request.method == 'DELETE':
            content = parser_json_volumes.parse_args()
            if content['action'] == 'delete':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    app.logger.info('Deleting volume claim')
                    volume_management_delete = VolumesManagementDelete(auth_dict)
                    # delete the volume claim
                    dat = volume_management_delete.persistent_volume_claim_delete(volume_name,
                                                                                  content['options']['namespace'])
                    # delete de volume class
                    if content['options']['volume_class']:
                        app.logger.info('Deleting volume class')
                        volume_management_delete.persistent_volume_class_delete(content['options']['volume_class'])

                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp


# adding arguments to be parsed for secretes
parser_json_secrets = api.parser()
parser_json_secrets.add_argument('action', type=str, required=True, help='Action')
parser_json_secrets.add_argument('options', type=dict, required=True,
                                 help='Options, eg: "options": {"namespace":"ns-staging", "data":{"username":"admin", "password":"test"}}')


@api.route('/api/kube/secrets/<string:secret_name>', endpoint='secrets')
@api.doc(parser=parser_json_secrets)
class Secrets(Resource):
    @staticmethod
    @require_token_role
    def post(secret_name):
        '''Secrets management (create/patch)

        Secret create:
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"namespace":"ns-staging", "data":{"username":"admin", "password":"test"}}}' http://localhost:5000/api/kube/secrets/mysecret

        :param secret_name:
        :return:
        '''
        if request.method == 'POST':
            content = parser_json_secrets.parse_args()
            if content['action'] == 'create':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    secrets_management_create = SecretsManagementCreate(auth_dict)
                    # create secrets object
                    secrets__obj = secrets_management_create.secret_object(secret_name,
                                                                           content['options']['data'])

                    # create secrets
                    dat = str(secrets_management_create.create_secret(secret_name, content['options']['namespace'],
                                                                      secrets__obj))
                    app.logger.info(
                        'Secret:{1} in namespace:{0} created'.format(
                            content['options']['namespace'], secret_name))

                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp

    @staticmethod
    @require_token_role
    def delete(secret_name):
        '''Secrets management (delete)

        Delete secret:
        curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete","options": {"namespace":"ns-staging"}}' http://localhost:5000/api/kube/secrets/mysecret
        :return:
        '''
        if request.method == 'DELETE':
            content = parser_json_secrets.parse_args()
            if content['action'] == 'delete':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    secret_management_delete = SecretsManagementDelete(auth_dict)
                    # need to convert object returned by kube api to string
                    dat = str(secret_management_delete.delete_secret(secret_name, content['options']['namespace']))

                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp


parser_json_scale = api.parser()
parser_json_scale.add_argument('action', type=str, required=True, help='Action')
parser_json_scale.add_argument('options', type=dict, required=True,
                               help='Options, eg: "options": {"namespace":"ns-staging", "deployment_name":"nginx-deploy","max_replicas":"5", "cpu_utilization":"1"}')


@api.route('/api/kube/scale/<string:scale_name>', endpoint='scale')
@api.doc(parser=parser_json_secrets)
class Scale(Resource):
    @staticmethod
    @require_token_role
    def post(scale_name):
        '''Enable horizontal scaling for a deployment

        New scaling
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create","options": {"namespace":"ns-staging", "deployment_name":"nginx-deploy","max_replicas":"5", "cpu_utilization":"1"}}' http://localhost:5000/api/kube/scale/myscale
        Update scaling (yes, same options params required)
        $ curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X POST -d '{"action":"create","options": {"namespace":"ns-staging", "deployment_name":"nginx-deploy","max_replicas":"7", "cpu_utilization":"80"}}' http://localhost:5000/api/kube/scale/myscale
        :return:
        '''
        if request.method == 'POST':
            content = parser_json_scale.parse_args()
            app.logger.info('Scale up')
            scale = ScalingManagementCreate(auth_dict, content['options']['deployment_name'],
                                            content['options']['max_replicas'], content['options']['cpu_utilization'])

            obj_scale = scale.create_scaling_object(scale_name)
            dat = str(scale.create_scaling(scale_name, obj_scale, content['options']['namespace']))
            resp = Response(response=dat, status=200, mimetype='application/json')
            return resp

    @staticmethod
    @require_token_role
    def delete(scale_name):
        '''Scale management (delete)

        Delete scale:
        curl -i  -H "token:eyJhbGciOi" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete","options": {"namespace":"ns-staging"}}' http://localhost:5000/api/kube/scale/myscale
        :return:
        '''
        if request.method == 'DELETE':
            content = parser_json_secrets.parse_args()
            if content['action'] == 'delete':
                if not content['options']:
                    app.logger.info('options values required')
                    dat = 'Options values must be specified'
                else:
                    scale_management_delete = ScalingManagementDelete(auth_dict)
                    # need to convert object returned by kube api to string
                    dat = str(scale_management_delete.scale_delete(scale_name, content['options']['namespace']))

                resp = Response(response=dat, status=200, mimetype='application/json')
                return resp


if __name__ == '__main__':
    # set the app settings env variables
    # Ex: for dev env: export APP_SETTINGS="config.DevelopmentConfig"
    app.config.from_object(os.environ.get('APP_SETTINGS', config.DevelopmentConfig))
    # load dashboard for production env only (eg: export APP_SETTINGS="config.DevelopmentConfig")
    # start main app
    port = int(os.environ.get('PORT', 5000))
    # by default flask is threaded enabled
    app.run(host='0.0.0.0', port=port, threaded=True)
