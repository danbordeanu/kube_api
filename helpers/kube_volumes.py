from kubernetes import client
from kubernetes.client.rest import ApiException
from InitData import InitData


class VolumesManagementCreate(InitData):
    def __init__(self, auth_dict):
        # TODO Add constructor params, atm empty
        super(VolumesManagementCreate, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    @staticmethod
    def create_storage_class_object(storage_class_name, namespace):
        '''
        :param storage_class_name:
        :param namespace:
        :return:
        '''
        storage_obj = client.V1StorageClass(api_version='storage.k8s.io/v1',
                                            metadata=client.V1ObjectMeta(name=storage_class_name, namespace=namespace),
                                            mount_options=['dir_mode=0777', 'file_mode=0777', 'uid=1000', 'gid=1000'],
                                            parameters={'skuName': 'Standard_LRS'},
                                            provisioner='kubernetes.io/azure-file',
                                            kind='StorageClass'
                                            )
        return storage_obj

    def create_storage_class(self, storage_class_name, storage_obj, patch=False):
        try:
            api_response = self.storage.create_storage_class(body=storage_obj)
            dat = api_response
        except ApiException as e:
            if e.status == 409 and patch:
                # 409 error message is for Conflict, patch the storage class if patch is true
                # btw, we love EAFP :P
                try:
                    api_response = self.storage.patch_storage_class(name=storage_class_name, body=storage_obj)
                    dat = api_response
                except ApiException as e:
                    dat = 'issue patching the storage class:{0}'.format(e)
            else:
                dat = 'issue creating storage class:{0}'.format(e)
        return dat

    def persistent_volume(self, volume_name, size, host_path, namespace, storage_class, patch=False):
        '''Create persistent volume by default on host.
        :param volume_name: nginx-volume
        :param size: 2Gi
        :param host_path: /mnt/azure
        :param namespace: ns-staging
        :param storage_class: nginx-storage
        :param patch: False
        :return:
        '''
        spec = client.V1PersistentVolumeSpec(capacity={'storage': size}, access_modes=['ReadWriteMany'],
                                             storage_class_name=storage_class,
                                             persistent_volume_reclaim_policy='Delete',
                                             host_path=client.V1HostPathVolumeSource(path=host_path))

        ps_vol = client.V1PersistentVolume(kind='PersistentVolume', api_version='v1',
                                           metadata=client.V1ObjectMeta(name=volume_name,
                                                                        namespace=namespace),
                                           spec=spec)

        try:
            api_response = self.v1.create_persistent_volume(body=ps_vol)
            dat = api_response
        except ApiException as e:
            if e.status == 409 and patch:
                # 409 error message is for Conflict, patch the storage class if patch is true
                # btw, we love EAFP :P
                try:
                    api_response = self.v1.patch_persistent_volume(name=volume_name, body=ps_vol)
                    dat = api_response
                except ApiException as e:
                    dat = 'issue patching persistent volume:{0}'.format(e)
            else:
                dat = 'issue creating persistent volume {0}'.format(e)
        return dat

    def persistent_volume_claim(self, volume_claim_name, size, storage_class, namespace):
        '''Create a volume claim.
        :param volume_claim_name: nginx-volume
        :param size: 2Gi
        :param storage_class: nginx-storage
        :param namespace: ns-staging
        :return:
        '''
        spec = client.V1PersistentVolumeClaimSpec(access_modes=['ReadWriteMany'],
                                                  storage_class_name=storage_class,
                                                  resources=client.V1ResourceRequirements(requests={'storage': size}))

        claim_vol = client.V1PersistentVolumeClaim(kind='PersistentVolumeClaim', api_version='v1',
                                                   metadata=client.V1ObjectMeta(name=volume_claim_name), spec=spec)
        try:
            api_response = self.v1.create_namespaced_persistent_volume_claim(namespace=namespace, body=claim_vol)
            dat = api_response
        except ApiException as e:
            if e.status == 409:
                dat = 'there is already a volume claim with this name, move alone'
            else:
                dat = 'issue creating volume claim {0}'.format(e)
        return dat


class VolumesManagementDelete(InitData):
    def __init__(self, auth_dict):
        # TODO Add constructor params, atm empty
        super(VolumesManagementDelete, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def persistent_volume_claim_delete(self, volume_claim_name, namespace=None):
        '''Delete volume claim
        :param volume_claim_name:
        :param namespace:
        :return:
        '''

        try:
            if namespace is None:
                namespace = 'default'

            api_response = self.v1.delete_namespaced_persistent_volume_claim(name=volume_claim_name,
                                                                             namespace=namespace,
                                                                             body=client.V1DeleteOptions(
                                                                                 propagation_policy='Foreground',
                                                                                 grace_period_seconds=5))
            dat = api_response.status
        except ApiException as e:
            dat = 'Issue:{0} deleting volume claim:{1}'.format(e, volume_claim_name)
        return dat

    def persistent_volume_class_delete(self, volume_class_name):
        '''Delete volume class
        :param volume_class_name:
        :param namespace:
        :return:
        '''

        try:

            api_response = self.storage.delete_storage_class(name=volume_class_name,
                                                             body=client.V1DeleteOptions(
                                                                 propagation_policy='Foreground',
                                                                 grace_period_seconds=5))
            dat = api_response.status
        except ApiException as e:
            dat = 'Issue:{0} deleting volume class:{1}'.format(e, volume_class_name)
        return dat
