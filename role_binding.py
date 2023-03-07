# Simple script to create roles and bind to specific namespaces

# auth string
from helpers.kube_auth_string import KubeAuthString
from helpers.kube_role_binding import RoleBindingManagement
import argparse


class RoleBinding(object):
    def __init__(self, username, namespace):
        self.auth_stuff = KubeAuthString()
        self.auth_dict = self.auth_stuff.give_me_auth_values()

        assert isinstance(username, object)
        self.username = username
        assert isinstance(namespace, object)
        self.namespace = namespace

        self.binding_management = RoleBindingManagement(self.auth_dict, self.username, self.namespace)

    def create_role_and_role_bindings(self):
        '''
        :return:
        '''
        # type: () -> object
        print 'Create role:{0} and bind to namespace:{1}'.format(self.username, self.namespace)
        self.binding_management.create_role(self.binding_management.create_user_role_object())
        self.binding_management.create_user_role_binding(self.binding_management.create_user_role_binding_object())

    def create_role_binding_with_role_reference(self, roleref):
        '''
        :param roleref:
        :return:
        '''
        print 'Create binding for role reference:{0} and bind to namespace:{1}'.format(roleref, self.namespace)
        self.binding_management.create_user_role_binding(self.binding_management.create_user_role_binding_object(roleref))

    def create_role(self):
        '''
        :return:
        '''
        # type: () -> object
        print 'Create role:{0}'.format(self.username)
        self.binding_management.create_role(self.binding_management.create_user_role_object())

    def delete_role_and_role_bindings(self):
        '''
        :return:
        '''
        print 'Delete role:{0} and unbind from namespace:{1}'.format(self.username, self.namespace)
        self.binding_management.delete_role()
        self.binding_management.delete_role_binding()

    def delete_role(self):
        '''
        :return:
        '''
        print 'Delete role:{0}'.format(self.username)
        self.binding_management.delete_role()

    def delete_role_bindings(self):
        '''
        :return:
        '''
        print 'Delete role bindings:{0} and unbind from namespace:{1}'.format(self.username, self.namespace)
        self.binding_management.delete_role_binding()

    def list_role(self):
        '''
        :return:
        '''
        print 'Print namespaced roles:{0}'.format(self.binding_management.list_namespace_role())

    def list_role_bindings(self):
        '''
        :return:
        '''
        print 'Print namespaced role bindings:{0}'.format(self.binding_management.list_namespace_role_binding())


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', required=False, type=str, metavar='role', help='Create Role')
    parser.add_argument('--username', required=False, type=str, metavar='username', help='Username')
    parser.add_argument('--namespace', required=True, type=str, metavar='namespace', help='Namespace')
    parser.add_argument('--action', required=True, type=str, metavar='action', help='Action to perform, '
                                                                                    'create/delete/list/bind')
    args = parser.parse_args()

    # I know, it's crazy, but it has to be like this

    # do generic role in the specific namespace
    # ex: python role_binding.py --role=supergeneric --namespace=ns-staging --action=create
    if args.action == 'create' and args.role and args.username is None:
        binduser = RoleBinding(args.role, args.namespace)
        binduser.create_role()

    # delete a generic role from a namespace
    # ex: python role_binding.py --role=supergeneric --namespace=ns-staging --action=delete
    if args.action == 'delete' and args.role and args.username is None:
        binduser = RoleBinding(args.role, args.namespace)
        binduser.delete_role()

    # create role with username and do the binding
    # ex: python role_binding.py --role=xxxx --username=xxx --namespace=ns-staging --action=create
    if args.action == 'create' and args.username and args.role:
        binduser = RoleBinding(args.username, args.namespace)
        binduser.create_role_and_role_bindings()

    # bind username to the generic role in a namespace
    # ex: python role_binding.py --role=supergeneric --username=xxxx --namespace=ns-staging --action=bind
    if args.action == 'bind' and args.username and args.role:
        binduser = RoleBinding(args.username, args.namespace)
        binduser.create_role_binding_with_role_reference(args.role)

    # unbind username from a generic role in a namespace
    # ex: python role_binding.py --role=supergeneric --username=xxxx --namespace=ns-staging --action=unbind
    if args.action == 'unbind' and args.username and args.role:
        binduser = RoleBinding(args.username, args.namespace)
        binduser.delete_role_bindings()

    # delete role and binding for a user
    # ex: python role_binding.py --role=xxxx --username=xxxx --namespace=ns-staging --action=delete
    if args.action == 'delete' and args.username and args.role:
        binduser = RoleBinding(args.username, args.namespace)
        binduser.delete_role_and_role_bindings()

    # list roles and role bindings
    if args.action == 'list':
        binduser = RoleBinding(args.role, args.namespace)
        binduser.list_role()
        binduser.list_role_bindings()
