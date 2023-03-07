#!!!!NB!!!! THIS IS A GENERIC/EXAMPLE TEMPLATE  THAT WILL BE USED FOR THE KUBE CALLS


from kubernetes.client.rest import ApiException
from InitData import InitData


class GenericManagement(InitData):
    def __init__(self, auth_dict):
        super(GenericManagement, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def generic_create(self, generic_name):
        '''

        :param generic_name:
        :return:
        '''
        # print the values from InitData
        try:
            dat = 'Generic: {0} created'.format(generic_name)
        except ApiException as e:
            dat = 'Issue:{0} creating the generic:{1}'.format(e, generic_name)
        return dat
