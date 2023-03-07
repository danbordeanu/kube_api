from kubernetes.client.rest import ApiException
from InitData import InitData
import json


class PodsManagement(InitData):
    def __init__(self, auth_dict):
        super(PodsManagement, self).__init__(auth_dict)
        '''
        auth and connection strings
        :param auth_dict:
        '''

    def pods_list(self, namespace_name, label=None):
        '''
        list pods from a specific namespae
        :param namespace_name:
        :param label
        :return:
        '''
        try:
            # check if label is set and list namespace based on the label selector
            if label:
                pod_list = self.v1.list_namespaced_pod(namespace_name, label_selector='app={}'.format(label))
            else:
                pod_list = self.v1.list_namespaced_pod(namespace_name)

            output = []
            for pod in pod_list.items:
                # build nested dict
                nested_dict = {'pods': dict(name=pod.metadata.name, state=pod.status.phase, ip=pod.status.pod_ip)}
                output.append(nested_dict)
            # if output is 0 maybe the namespace is wrong/doesn't exists
            if not output:
                dat = 'Empty response, maybe wrong namespace'
            else:
                dat = json.dumps(output)
        except ApiException as e:
            dat = 'Issue:{0} listing the pods for the namespace:{1}'.format(e, namespace_name)
        return dat

    def pods_logs(self, podname, namespace, tail_lines=None, since_seconds=None, pretty=None):
        '''
        read pod logs
        :param namespace:
        :param podname:
        :param pretty:  # str | If 'true', then the output is pretty printed. (optional)
        :param tail_lines: # If set, the number of lines from the end of the logs to show. If not specified, logs are shown from the creation of the container or sinceSeconds or sinceTime (optional)
        :param since_seconds: # A relative time in seconds before the current time from which to show logs. If this value precedes the time a pod was started, only logs since the pod start will be returned. If this value is in the future, no logs will be returned. Only one of sinceSeconds or sinceTime may be specified. (optional)
        :return:
        '''
        try:
            output_log = []

            if tail_lines:
                tail_lines = tail_lines
            else:
                # last 56 lines
                tail_lines = 56

            if since_seconds:
                since_seconds = since_seconds
            else:
                # logs 10 min back
                since_seconds = 600

            if pretty:
                # str | If 'true', then the output is pretty printed. (optional)
                pretty = 'pretty_example'
            else:
                pretty = ''

            pod_logs = self.v1.read_namespaced_pod_log(name=podname, namespace=namespace, tail_lines=tail_lines,
                                                       since_seconds=since_seconds, pretty=pretty)

            output_log.append(pod_logs)
            if not output_log:
                dat = 'Empty response, maybe wrong namespace'
            else:
                dat = output_log
        except ApiException as e:
            dat = 'Issue:{0} listing the pods for the namespace:{1}'.format(e, namespace)
        return dat
