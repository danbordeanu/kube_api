import os
from kubernetes import client
from kubernetes.client.rest import ApiException
from InitData import InitData
from helpers import config_parser as parser


class DeploymentsManagementCreate(InitData):
    def __init__(self, auth_dict, container_name, container_image, container_port, metadata_labels, replicas,
                 mount_path, volume_claim, env, env_secret, command, args, resources):
        super(DeploymentsManagementCreate, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

        if resources:
            resources = resources
        else:
            limits_memory = os.getenv('DEPLOYMENT_LIMITS_MEMORY', parser.config_params('deployment')['limits_memory'])
            limits_cpu = os.getenv('DEPLOYMENT_LIMITS_CPU', parser.config_params('deployment')['limits_cpu'])

            requests_memory = os.getenv('DEPLOYMENT_REQUESTS_MEMORY',
                                        parser.config_params('deployment')['requests_memory'])
            requests_cpu = os.getenv('DEPLOYMENT_REQUESTS_CPU', parser.config_params('deployment')['requests_cpu'])

            resources = {"limits": {"memory": limits_memory, "cpu": limits_cpu},
                         "requests": {"memory": requests_memory, "cpu": requests_cpu}}

        # this will create a list of dictionaries used into pod specs
        env_var_list = []
        for k, v in env.items():
            env_var_list.append(client.V1EnvVar(name=k, value=v))

        # convert command from string to list
        if command:
            command = command.strip('][').split(', ')
        else:
            command = []
        # convert command args string to list
        if args:
            args = args.strip('][').split(', ')
        else:
            args = []

        # THIS IS SETTING ENV VAR USERNAME FROM SECRET:MYSECRET WITH THE KEY VALUE USERNAME

        # env_secret = {'username': {'mysecret': 'username'}, 'password': {'mysecret': 'password'}}
        # env_Secret is nested dict
        if env_secret:
            for k, v in env_secret.items():
                for kk, vv in v.items():
                    env_var_list.append(client.V1EnvVar(name=k,
                                                        value_from=client.V1EnvVarSource(
                                                            secret_key_ref=client.V1SecretKeySelector(name=kk,
                                                                                                      key=vv))))

        # create deployment with smb mount
        if mount_path and volume_claim:
            # Configure Pod template container
            self.container = client.V1Container(
                name=container_name,
                image=container_image,
                resources=resources,
                env=env_var_list,
                command=command,
                args=args,
                volume_mounts=[client.V1VolumeMount(mount_path=mount_path, name='volumes', read_only=False)],
                ports=[client.V1ContainerPort(container_port=int(container_port))])

            # Create and configure a spec section
            self.template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={'app': metadata_labels}),
                spec=client.V1PodSpec(containers=[self.container],
                                      volumes=[client.V1Volume(name='volumes',
                                                               persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                                                   claim_name=volume_claim))]))
        # create deployment without smb mount
        else:
            # Configure Pod template container
            self.container = client.V1Container(
                name=container_name,
                image=container_image,
                resources=resources,
                env=env_var_list,
                command=command,
                args=args,
                ports=[client.V1ContainerPort(container_port=int(container_port))])

            # Create and configure a spec section
            self.template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={'app': metadata_labels}),
                spec=client.V1PodSpec(containers=[self.container]))

        # Create the specification of deployment
        self.spec = client.V1DeploymentSpec(selector=client.V1LabelSelector(match_labels={'app': metadata_labels}),
            replicas=int(replicas),
            template=self.template)

        # app labels
        self.metadata_labels = metadata_labels

    def create_deployment_object(self, deployment_name):
        '''
        :param deployment_name:
        :return:
        '''

        # Instantiate the deployment object
        deployment = client.V1Deployment(
            api_version='apps/v1',
            kind='Deployment',
            metadata=client.V1ObjectMeta(name=str(deployment_name), labels={'app': self.metadata_labels}),
            spec=self.spec)

        return deployment

    def create_deployment(self, deployment, namespace, patch=False, deployment_name=None):
        '''
        Create deployement
        :param deployment:
        :param deployment_name
        :param namespace:
        :param patch
        :return:
        '''
        try:
            api_response = self.v1_extension.create_namespaced_deployment(body=deployment, namespace=namespace)
            dat = api_response.status
        except ApiException as e:
            # if return code is 409 deployment already created, trying to update
            if e.status == 409 and patch:
                try:
                    # patch the deployment
                    api_response = self.v1_extension.patch_namespaced_deployment(name=deployment_name,
                                                                                 body=deployment, namespace=namespace)
                    dat = api_response.status
                except ApiException as e:
                    dat = 'issue:{0} patching deployment:{1}'.format(e, deployment)
            else:
                dat = 'Issue:{0} creating deployment:{1}'.format(e, deployment)
        return dat


# TODO remove this part, is become useless since update is merged in create


class DeploymentsManagementUpdate(InitData):
    # TODO this class is OUTDATED it has the same functionality like the create class
    def __init__(self, auth_dict, container_name, container_image, container_port, metadata_labels, replicas):
        super(DeploymentsManagementUpdate, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''
        # Configure Pod template container
        self.container = client.V1Container(
            name=container_name,
            image=container_image,
            ports=[client.V1ContainerPort(container_port=int(container_port))])

        # Create and configurate a spec section
        # TODO add also resources limits here
        self.template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={'app': metadata_labels}),
            spec=client.V1PodSpec(containers=[self.container]))

        # Create the specification of deployment
        self.spec = client.V1DeploymentSpec(selector=client.V1LabelSelector(match_labels={'app': metadata_labels}),
            replicas=int(replicas),
            template=self.template)

        # app labels
        self.metadata_labels = metadata_labels

    def create_deployment_object(self, deployment_name):
        '''
        :param deployment_name:
        :return:
        '''

        # Instantiate the deployment object
        aaa = client.V1Deployment
        deployment = client.V1Deployment(
            api_version='apps/v1',
            kind='Deployment',
            metadata=client.V1ObjectMeta(name=str(deployment_name), labels={'app': self.metadata_labels}),
            spec=self.spec)
        return deployment

    def update_deployment(self, deployment, deployment_name, namespace):
        '''
        update deployment
        :param deployment:
        :param deployment_name
        :param namespace:
        :return:
        '''

        try:
            api_response = self.v1_extension.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment)

            dat = str(api_response.status)
        except ApiException as e:
            dat = 'Issue:{0} updating deployment:{1}'.format(e, deployment_name)
        return dat


class DeploymentsManagementDelete(InitData):
    def __init__(self, auth_dict):
        super(DeploymentsManagementDelete, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def delete_deployment(self, deployment, namespace=None):
        '''
        Delete deployment
        :param deployment:
        :param namespace
        :return:
        '''
        try:
            # if namespace is not provided we assume it will be the default namespace
            if namespace is None:
                namespace = 'default'

            api_response = self.v1_extension.delete_namespaced_deployment(
                name=deployment,
                namespace=namespace,
                body=client.V1DeleteOptions(
                    propagation_policy='Foreground',
                    grace_period_seconds=5))
            dat = api_response.status
        except ApiException as e:
            dat = 'Issue:{0} deleting deployment:{1}'.format(e, deployment)
        return dat


class DeploymentsManagementList(InitData):
    def __init__(self, auth_dict):
        super(DeploymentsManagementList, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def list_deployment(self, label_selector, namespace=None):
        '''
        List deployments
        :param label_selector:
        :param namespace
        :return:
        '''
        try:
            # if namespace is not provided we assume it will be the default namespace
            if namespace is None:
                namespace = 'default'
            api_response = self.v1_extension.list_namespaced_deployment(namespace=namespace,
                                                                        label_selector=label_selector)
            dat = api_response
        except ApiException as e:
            dat = 'Issue:{0} list  deployment with label:{1}'.format(e, label_selector)
        return dat
