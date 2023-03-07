from threading import Thread
from pymemcache.client import base
from memcached_stats import MemcachedStats
import tornado.web
from helpers import logger_settings
import pika
import json
from tornado import websocket
import uuid
from Variables import VariablesShared
import ast


class UserSubscribeJobId(tornado.web.RequestHandler):
    # ENDPOINT request jobId
    def data_received(self, chunk):
        pass

    def get(self):
        userid = str(self.get_argument('userid'))
        service = str(self.get_argument('service'))
        namespace = str(self.get_argument('namespace'))
        assert isinstance(userid, str), 'Need user name in GET request'
        assert isinstance(service, str), 'Need service in GET request'
        assert isinstance(namespace, str), 'Need namespace in GET request'

        # Writing all data for the api call in a single struct: data
        data = json.dumps({'userid': userid, 'service': service, 'namespace': namespace})
        logger_settings.logger.info('GET - [namespace, user,service]- {0}:{1}:{2}'.format(namespace, userid, service))

        # json rest answer 
        self.write(data)

        # Sending the struct 'data' to the queue
        try:
            rabbit = pika.BlockingConnection(VariablesShared.connection_settings)
            channel_global = rabbit.channel()
            channel_global.basic_publish(exchange='', routing_key=VariablesShared.queue_first,
                                                         body=data)
        except Exception as e:
            logger_settings.logger.error(
                'REST_tornado/UserSubscribeJobId - Issues publishing to the rabbitmq queue:{0}'.format(e))


# ENDPOINT websocket manager
class WebsocketConnectionMangerEndPoint(websocket.WebSocketHandler):

    # following two methods are inhereited and must be there  (maybe)
    def data_received(self, chunk):
        pass

    def check_origin(self, origin):
        return True

    def __init__(self, application, request, **kwargs):
        self.iteration = 1
        # TODO: we are not inheriting so we only need to initialize here not the user
        super(WebsocketConnectionMangerEndPoint, self).__init__(application, request, **kwargs)
        # random string used for as the logging token
        self.client_id = str(uuid.uuid4())
        self.userid = ''

        # Storing the list of users with sockets 
        self.sockets = []

    # Client connects and open a websocket -------------------------------------
    def open(self):
        x_real_ip = self.request.headers.get('X-Real-IP')
        remote_ip = x_real_ip or self.request.remote_ip
        logger_settings.logger.info(
            'REST_tornado/open - connection for client {0} opened and ip: {1}...'.format(self.client_id, remote_ip))
        self.createsession(self)  # storing web socket object for further communication with client

    # When client writes to websocket this method is called (like a callback)
    def on_message(self, message):
        pass
        # logger_settings.logger.info('REST_tornado/WebsocketConnectionMangerEndPoint/on_message - Message received:{0}'.format(message))

    # When user closes the websockeet this method is calledc (callback )
    def on_close(self):
        self.deletesession(self)

        # Memcached WATCHER

    # TODO spawn several processes???
    def memcache_watcher(self, userid, mysocket):

        self.iteration = 1

        logger_settings.logger.debug(
            'REST_tornado/WebsocketConnectionMangerEndPoint/memcache_watcher - [userid, mysocket]: {0} {1}'.format(
                userid, mysocket))

        try:
            clients_ready = base.Client((VariablesShared.mem_cache_host, int(VariablesShared.mem_cache_port)))
            mem = MemcachedStats(VariablesShared.mem_cache_host, VariablesShared.mem_cache_port)

            while True:

                #time.sleep(0.1)  # DO NOT remove!!! neccesary for memccache

                # logger_settings.logger.debug('memcache_watcher is trying with keys {0}'.format(mem.keys()))
                # print clients_ready.get('userid')
                # print "socket"
                # print type(mysocket)
                # for key, value in mysocket.iteritems():
                # print("REST_tornado/memcache_watcher - userid: {0}".format(mysocket.get(key)))
                for user in mem.keys():
                    # print("ALL we have in main [userid: object]   {0} : {1} ".format(user, clients_ready.get(user)))
                    if userid == user:

                        try:
                            # this is converting the blob data/str from memcache into a tuple of dicts
                            blob = ast.literal_eval((clients_ready.get(user).replace('}', '},'))[:-1])
                            # logger_settings.logger.info('REST_tornado/memcache_watcher writing to socket for request number {0}'.format(self.iteration))
                            self.iteration = self.iteration + 1
                            #now let's iterate in blob and get all dict and put them on socket
                            if isinstance(blob, dict):
                                ret_str = json.dumps([{'REST_tornado - servicestatus: ': blob},
                                                      {' Iteration ': self.iteration}])
                                mysocket['wsobj'].write_message(ret_str)
                            else:
                                for blob_iter in blob:
                                    ret_str = json.dumps([{'REST_tornado - servicestatus: ': blob_iter},
                                                          {' Iteration ': self.iteration}])
                                    mysocket['wsobj'].write_message(ret_str)
                            if clients_ready.get(userid) is not None:
                                clients_ready.delete(userid)
                            else:
                                logger_settings.logger.info('No data to delete from memcached, move alone, nothing do to')
                        except Exception as e:
                            pass
                            # logger_settings.logger.error(
                            #     'REST_tornado/memcache_watcher - Issues writing to the socket...panic:{0}'.format(e))
        except Exception:
            logger_settings.logger.error('REST_tornado/memcache_watcher - Issues creating the memcache connection')

    # Create a websocket session and stores it in an array
    def createsession(self, obj):

        self.userid = str(obj.get_argument('userid'))
        logger_settings.logger.info('Creating websocket for user: {0}'.format(self.userid))
        assert isinstance(self.userid, str), 'Need user name when registering socket'

        self.sockets.append(dict(wsobj=obj, userid=self.userid))
        mysocket = dict(wsobj=obj, userid=self.userid)

        t = Thread(target=self.memcache_watcher, args=(self.userid, mysocket))
        t.start()

    # Delete session from array when client refreshes the page or closes the page
    def deletesession(self, obj):
        try:
            for item in self.sockets:
                if obj == item['wsobj']:
                    self.sockets.remove(item)
        except Exception as e:
            raise e
