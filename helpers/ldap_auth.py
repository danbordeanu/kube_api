from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
import ldap
import os
from pymemcache.client import base
import base64
from helpers import config_parser as parser
from helpers import logger_settings


class LdapUserAuth(object):
    def __init__(self):
        # ldap server
        self.ldap_server = os.environ.get('LDAP_HOST', parser.config_params('ldap')['server'])
        # memcache server
        self.mem_cache_host = os.environ.get('MEMCACHED_HOST', parser.config_params('memcache')['host'])
        self.mem_cache_port = os.environ.get('MEMCACHED_PORT', parser.config_params('memcache')['port'])

    def check_ldap_password(self, username, password):
        try:
            # make connection to ldap endpoint
            # use ldaps
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            connection = ldap.initialize(self.ldap_server)
            ldap.set_option(ldap.OPT_REFERRALS, 0)
            ldap.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            ldap.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
            ldap.set_option(ldap.OPT_X_TLS_DEMAND, True)
            # try to bind using user/passwd
            connection.simple_bind_s(username, base64.b64decode(password))
            connection.set_option(ldap.OPT_REFERRALS, 0)
            # perform simple search in ldap

            search_filter = '(&(objectClass=user)(sAMAccountName=' + username.split('@')[0] + '))'

            # look into people OU
            result_people = connection.search_s('OU=Office,OU=People Accounts,DC=domain,DC=com',
                                                ldap.SCOPE_ONELEVEL,
                                                search_filter)

            # look into NP Accounts
            result_tech_user = connection.search_s('OU=accounts,DC=domain,DC=com', ldap.SCOPE_ONELEVEL,
                                                   search_filter)

            # debbuging messages
            logger_settings.logger.debug('People:{0}'.format(result_people))
            logger_settings.logger.debug('Tech Account:{0}'.format(result_tech_user))

            # if there is info about the user/npa generate the token
            if result_people or result_tech_user:

                # generate token
                logger_settings.logger.info('User:{0} got authenticated'.format(username))
                token = self.generate_auth_token(username)
                # logger_settings.logger.debug('What we found about user in ldap:{0}'.format(result))
                # insert into memcache
                self.insert_token_memcache(username, token)
                # return generated token to the rest/api
                return token
            else:
                logger_settings.logger.info(
                    'There is no info in ldap about this user, that is very strange:{0}'.format(result_people))
                # force unbind
                connection.unbind()
                return None
        except (ldap.INVALID_CREDENTIALS, ldap.CONNECT_ERROR, ldap.SERVER_DOWN, TypeError) as e:
            logger_settings.logger.info('Issue connecting to ldap:{0}'.format(e))
            token = 'Issue connecting to ldap:{0}'.format(e)
            return token

    @staticmethod
    def generate_auth_token(username):
        '''
        :param username:
        :return:
        '''
        s = Serializer(parser.config_params('ldap')['secret_key'],
                       expires_in=int(parser.config_params('ldap')['expire_interval']))
        logger_settings.logger.info('Token generated for user:{0}'.format(username))
        return s.dumps(dict(username=username))

    @staticmethod
    def verify_auth_token(token):
        '''
        :param token:
        :return:
        '''
        s = Serializer(parser.config_params('ldap')['secret_key'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired, TypeError):
            logger_settings.logger.info('Seems token is invalid or expired, need to login again')
            return None

        return data['username']

    def insert_token_memcache(self, username, token):
        '''
        :param username:
        :param token:
        :return:
        '''
        try:
            clients_ready = base.Client((self.mem_cache_host, int(self.mem_cache_port)), connect_timeout=10, timeout=10,
                                        no_delay=True)
            # Writing to memcached
            # set(only one token per user) data with the same exp value from config
            clients_ready.set(username, token, int(parser.config_params('ldap')['expire_interval']))
            logger_settings.logger.debug(
                'Token for user:{0} added to memcached'.format(username))
        except Exception as e:
            logger_settings.logger.debug('Issue writing to memcached:{0}'.format(e))

    def get_token_memcache(self, username):
        '''
        :param username:
        :return:
        '''
        try:
            clients_ready = base.Client((self.mem_cache_host, int(self.mem_cache_port)))
            token = clients_ready.get(username)
            if token:
                logger_settings.logger.info('Got token:{0} for user:{1}'.format(token, username))
                return token
            else:
                logger_settings.logger.info('No token for user:{0} in memcache'.format(username))

        except Exception as e:
            logger_settings.logger.debug('Issue getting token from memcached:{0}'.format(e))
