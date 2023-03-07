import requests
from helpers import logger_settings
from helpers.Error import KUBEError, ExceptionType
import json
import ast


def get_job_info(url, service, namespace):
    try:
        url = url + '/' + 'api' + '/kube/push'
        headers_info = {'Content-Type': 'application/json'}
        service_data = dict(action='read',
                            options={'namespace': namespace})
        r = requests.post(url + '/' + service, headers=headers_info,
                          data=json.dumps(service_data)).text
        returned_data_api = ast.literal_eval(r)
        data = returned_data_api['ip']
        assert isinstance(data, object)
        return data

    except requests.exceptions.Timeout as e:
        raise (KUBEError(ExceptionType.KUBEAPI_TIMEOUT, ' at get_service_ip [ {0} ]'.format(e)))

    except requests.exceptions.HTTPError as e:
        raise (KUBEError(ExceptionType.KUBEAPI_FORDBIDDEN, ' at get_service_ip [ {0} ]'.format(e)))

    except requests.exceptions.TooManyRedirects as e:
        raise (KUBEError(ExceptionType.KUBEAPI_TOOMANYREDIRECTS, ' at get_service_ip [ {0} ]'.format(e)))

    except requests.exceptions.RequestException as e:
        raise (KUBEError(ExceptionType.KUBEAPI_OTHER, ' at get_service_ip [ {0} ]'.format(e)))

    except Exception:
        logger_settings.logger.debug('No idea, maybe service not ready yet, just wait a while')
        raise (KUBEError(ExceptionType.KUBEAPI, ' at get_service_ip'))

