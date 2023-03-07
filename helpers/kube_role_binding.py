from kubernetes import client
from kubernetes.client.rest import ApiException
from InitData import InitData


# handling role binding
class RoleBindingManagement(InitData):
    def __init__(self, auth_dict, username, namespace):
        super(RoleBindingManagement, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

        # custom made rules
        # https://kubernetes.io/docs/reference/kubectl/overview/#resource-types
        self.rules = [
            client.V1PolicyRule(['', 'extensions', 'apps', 'autoscaling', 'sc', 'storage.k8s.io', 'batch'],
                                resources=['pods', 'pods/logs', 'pods/status', 'deployments', 'replicasets', 'secrets', 'hpa',
                                           'ingresses', 'services', 'storageclass', 'jobs', 'configmaps', 'cronjobs',
                                           'volumeattachments', 'persistentvolumeclaims', 'persistentvolumes',
                                           'resourcequotas'],
                                verbs=['get', 'list', 'create', 'delete', 'update', 'patch',
                                       'watch'])
        ]

        # all rules and verbs
        self.rules_all = [client.V1PolicyRule(api_groups=['*'], resources=['*'], verbs=['*'])]

        self.username = username
        self.namespace = namespace

        # name of role binding metadata
        self.name = 'reader-service'

    # Instantiate the role object
    def create_user_role_object(self):
        '''
        :param service_name:
        :return:
        '''
        # role object
        role = client.V1Role(rules=self.rules,
                             metadata=client.V1ObjectMeta(namespace=self.namespace, name=self.username))
        return role

    # Instantiate the role binding object
    def create_user_role_binding_object(self, roleref=None):
        '''
        :param roleref:
        :return:
        '''
        # role binding object

        if roleref:
            self.roleref=roleref
        else:
            self.roleref= self.username

        role_binding = client.V1RoleBinding(api_version='rbac.authorization.k8s.io/v1', kind='RoleBinding',
                                            metadata=client.V1ObjectMeta(namespace=self.namespace,
                                                                         name=self.name + '-' + self.username),
                                            subjects=[client.V1Subject(name=self.username, namespace=self.namespace,
                                                                       kind='User',
                                                                       api_group='rbac.authorization.k8s.io')],
                                            role_ref=client.V1RoleRef(api_group='rbac.authorization.k8s.io',
                                                                      kind='Role',
                                                                      name=self.roleref))

        return role_binding

    # create role
    def create_role(self, role):
        '''
        :param role:
        :return:
        '''
        try:
            api_response = self.rbac.create_namespaced_role(namespace=self.namespace, body=role)
            dat = api_response
        except ApiException as e:
            dat = 'Issue:{0} creating role:{0}'.format(e)
        return dat

    # create role binding, the created role must be bound to a user
    def create_user_role_binding(self, role_binding):
        '''
        :param role_binding:
        :return:
        '''
        try:
            api_response = self.rbac.create_namespaced_role_binding(namespace=self.namespace, body=role_binding)
            dat = api_response
        except ApiException as e:
            dat = 'Issue:{0} creating role binding:{0}'.format(e)
        return dat

    # list namespace roles
    def list_namespace_role(self):
        try:
            api_response = self.rbac.list_namespaced_role(self.namespace)
            dat = str(api_response)
        except ApiException as e:
            dat = 'Issue:{0} reading namespaced roles:{1}'.format(e, self.namespace)
        return dat

    # list namespace role bindings
    def list_namespace_role_binding(self):
        try:
            api_response = self.rbac.list_namespaced_role_binding(self.namespace)
            dat = str(api_response)
        except ApiException as e:
            dat = 'Issue:{0} reading namespaced role bindings:{1}'.format(e, self.namespace)
        return dat

    # delete role
    def delete_role(self):
        try:
            self.rbac.delete_namespaced_role(name=self.username, namespace=self.namespace,
                                             body=client.V1DeleteOptions())
            dat = 'Role {0} deleted'.format(self.namespace)
        except ApiException as e:
            dat = 'Issue:{0} deleting namespaced role:{1}'.format(e, self.namespace)
        return dat

    # delete role binding
    def delete_role_binding(self):
        try:
            self.rbac.delete_namespaced_role_binding(name=self.name + '-' + self.username,
                                                     namespace=self.namespace,
                                                     body=client.V1DeleteOptions())
            dat = 'Role binding {0} deleted'.format(self.namespace)
        except ApiException as e:
            dat = 'Issue:{0} deleting namespaced role binding:{1}'.format(e, self.namespace)
        return dat
