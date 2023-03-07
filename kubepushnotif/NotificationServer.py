from concurrent.futures import ThreadPoolExecutor
import time
import os
import tornado.ioloop
import tornado.web
import tornado
import ast
import sys
from multiprocessing import Process
import uuid

from pymemcache.client import base
from memcached_stats import MemcachedStats

from commons.Variables import VariablesShared
# Endpoints
from commons.REST_tornado import UserSubscribeJobId
from commons.REST_tornado import WebsocketConnectionMangerEndPoint
from commons.Kube_Endpoint import get_job_info
from commons.helpers import logger_settings


class KubeapiServiceIpMonitor(tornado.web.RequestHandler):
    def __init__(self, name=None):
        self.service = ''
        self.name = name
        self.futures = []

    def future_serviceIp_watcher(self, namespace, service, userid):
        self.pool = ThreadPoolExecutor(1)
        self.futures.append(self.pool.submit(self.handler_jobId, service, namespace, userid))

    def handler_jobId(self, service, namespace, userid):
        logger_settings.logger.info(
            'kubeapi_ServiceIp_monitor -  Starting IP status for user:{0} and service:{1}'.format(userid, service))
        while True:
            try:
                logger_settings.logger.debug(
                    'kubeapi_ServiceIp_monitor - :  service:{0} namespace:{1} userid:{2}'.format(service, namespace,
                                                                                                 userid))
                ip_status_result = (get_job_info(VariablesShared.url_kube, service, namespace))
            except Exception:
                logger_settings.logger.info(
                    'kubeapi_ServiceIp_monitor/handler_serviceIp - Exception on getting the IP of service {0}'.format(
                        service))
                break

            if VariablesShared.ip_monitor not in str(ip_status_result):
                logger_settings.logger.info(
                    'kubeapi_ServiceIp_monitor/handler_serviceIp - Waiting for service:{0} IP'.format(service))
                time.sleep(int(VariablesShared.pooling))
            else:
                logger_settings.logger.info(
                    'kubeapi_ServiceIp_monitor/handler_serviceIp - Service {0} has IP {1}'.format(service,
                                                                                                  ip_status_result))

                try:

                    clients_ready = base.Client((VariablesShared.mem_cache_host, int(VariablesShared.mem_cache_port)))
                    mem = MemcachedStats(VariablesShared.mem_cache_host, VariablesShared.mem_cache_port)

                    # Writing to memcached ---------------------------------------------
                    # dict with job status and job id to be written in memcache
                    making_the_data = {'IP': ip_status_result, 'SERVICE_NAME': service}
                    # if there is no userid we need to set it _first
                    if clients_ready.get(userid) is None:
                        clients_ready.set(userid, making_the_data)
                    else:
                        # THIS WILL GENERATE A STR containing all the jobs with status DONE
                        # if userid created/set already, we need to append data, this will generate a str
                        clients_ready.append(userid, making_the_data)
                    logger_settings.logger.debug(
                        'kubeapi_ServiceIp_monitor/handler_ServiceIp - to memcached  {0}'.format(
                            making_the_data))


                except Exception:
                    logger_settings.logger.debug(
                        'kubeapi_ServiceIp_monitor/handler_ServiceIp -  problem writing on the socket')
                # to break from the loop
                break


def QueueDispatcher(channel, method, properties, body):
    # Fetch from the queue (actually tornado automagically pushes here since QueueDispatcher is the official consumer of the queue)
    '''
    :param channel:
    :param method:
    :param properties:
    :param body:
    '''
    x = ast.literal_eval(body)
    monitor = KubeapiServiceIpMonitor()
    try:
        logger_settings.logger.debug('Do the ACK for first queue')
        VariablesShared.channel_global.basic_ack(
            delivery_tag=method.delivery_tag)  # To ack with the Queue to remove the message after processed
    except Exception:
        logger_settings.logger.error('Issues for ACK the stored event in the rabbitmq')

    monitor.future_serviceIp_watcher(x['namespace'], x['service'], x['userid'])
    logger_settings.logger.info('KUBEMonitorServer/QueueDispatcher - Reaching end of QueueDispatcher!')


class SetUpKubeMonitorServer(object):
    def __init__(self):
        # type: () -> object
        super(SetUpKubeMonitorServer, self).__init__()
        logger_settings.logger.info('Setting up the queue ')
        self.workers = []
        self.MAX_WORKERS = int(VariablesShared.MAX_WORKERS)
        self.init_queue()

    def init_queue(self):

        # durable = True -> When RabbitMQ quits or crashes it will NOT forget the queues and messages 
        # prefetch_count = 1 -> tells RabbitMQ not to give more than one message to a worker at a time
        # VariablesShared.channel_global.queue_declare(queue=VariablesShared.queue_first, durable=True)
        VariablesShared.channel_global.queue_declare(queue=VariablesShared.queue_first)
        VariablesShared.channel_global.basic_qos(prefetch_size=0, prefetch_count=1, all_channels=True)

        for i in range(self.MAX_WORKERS):
            p = Process(self.worker())
            self.workers.append(p)
            p.start()

    def worker(self):
        try:
            VariablesShared.channel_global.basic_consume(QueueDispatcher, queue=VariablesShared.queue_first)
            VariablesShared.channel_global.start_consuming()
        except Exception:
            logger_settings.logger.error('NotificationsServer/worker- issue creating the queue')

    def terminate(self):
        for i in range(self.MAX_WORKERS):
            self.workers(i).terminate()

    # TODO re-write
    # def alive(self):
    # return self.process.is_alive()
    # for i in range(self.MAX_WORKERS):
    # self.workers(i).terminate()


class SetUpNoticationsServer(object):
    def __init__(self):
        super(SetUpNoticationsServer, self).__init__()
        self.process = ''
        self.init_run_server()
        logger_settings.logger.info('Starting push notification service')

    def init_run_server(self):
        self.process = Process(target=self.worker)
        self.process.start()

    def worker(self):

        settings = {
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'cookie_secret': str(uuid.uuid4()),
            'xsrf_cookies': True,

        }

        self.http_server = tornado.web.Application([
            (r'/(favicon.png)', tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
            (r'/register', WebsocketConnectionMangerEndPoint),
            # Ex. var ws = new WebSocket("ws://localhost:8888/register?userid=bordeanu");
            (r'/push', UserSubscribeJobId),
            # Ex. userid=bordeanu&service=push-service&namespace=apc-staging
        ], **settings)

        try:
            # Starts the tornado object in a specific port after previous initialization
            self.http_server.listen(VariablesShared.app_port, VariablesShared.host)
            # Starts the listener for incoming requests from clients (webbrowser)
            tornado.ioloop.IOLoop.instance().start()
        except Exception, e:
            logger_settings.logger.error('Issues starting tornado {0}'.format(e))


if __name__ == '__main__':
    try:
        NotificationsServer = SetUpNoticationsServer()
        KubeMonitorServer = SetUpKubeMonitorServer()
    except KeyboardInterrupt:
        logger_settings.logger.info('Closing everything down')
        sys.exit(0)
