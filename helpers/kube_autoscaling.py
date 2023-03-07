from kubernetes import client
from kubernetes.client.rest import ApiException
from InitData import InitData


# handling autoscaling horizontally
class ScalingManagementCreate(InitData):
    def __init__(self, auth_dict, deployment_name, max_replicas, cpu_utilization):
        super(ScalingManagementCreate, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

        self.target = client.V1CrossVersionObjectReference(api_version='extensions/v1beta1',
                                                           kind='Deployment',
                                                           name=deployment_name)

        # Create the specification of horizon pod auto-scaling

        self.spec = client.V1HorizontalPodAutoscalerSpec(
            min_replicas=1,
            max_replicas=int(max_replicas),
            target_cpu_utilization_percentage=int(cpu_utilization),
            scale_target_ref=self.target)

    def create_scaling_object(self, autoscale_name):
        '''
        :param autoscale_name:
        :return:
        '''

        auto_scale_obj = client.V1HorizontalPodAutoscaler(
            api_version='autoscaling/v1',
            kind='HorizontalPodAutoscaler',
            spec=self.spec,
            metadata=client.V1ObjectMeta(name=autoscale_name))

        return auto_scale_obj

    def create_scaling(self, autoscale_name, auto_scale_obj, namespace_name, patch=True):
        '''
        :param autoscale_name:
        :param auto_scale_obj
        :param namespace_name:
        :param patch:
        :return:
        '''
        try:
            api_response = self.scale.create_namespaced_horizontal_pod_autoscaler(namespace=namespace_name,
                                                                                  body=auto_scale_obj)
            dat = api_response
        except ApiException as e:
            if e.status == 409 and patch:
                # 409 error message is for Conflict, patch the storage class if patch is true
                # btw, we love EAFP :P
                try:
                    api_response = self.scale.patch_namespaced_horizontal_pod_autoscaler(name=autoscale_name,
                                                                                         namespace=namespace_name,
                                                                                         body=auto_scale_obj)
                    dat = api_response
                except ApiException as e:
                    dat = 'issue patching scale:{0}'.format(e)
            else:
                dat = 'Issue:{0} creating horizontal scale'.format(e)
        return dat


class ScalingManagementDelete(InitData):
    def __init__(self, auth_dict):
        super(ScalingManagementDelete, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def scale_delete(self, scale_name, namespace=None):
        '''Delete scale
        :param scale_name:
        :param namespace:
        :return:
        '''

        try:
            if namespace is None:
                namespace = 'default'

            api_response = self.scale.delete_namespaced_horizontal_pod_autoscaler(name=scale_name, namespace=namespace,
                                                                                  body=client.V1DeleteOptions(
                                                                                      propagation_policy='Foreground',
                                                                                      grace_period_seconds=5))
            dat = api_response.status
        except ApiException as e:
            dat = 'Issue:{0} deleting horizontal scale:{1}'.format(e, scale_name)
        return dat
