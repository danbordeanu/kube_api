import base64
import yaml
import argparse
import os


class SslUtility(object):
    @staticmethod
    def read_config(configfile=None):
        '''
        read config file and return dict with the tls certs
        :param configfile:
        :return:
        '''
        if configfile:
            print 'Using config file from:{0}'.format(configfile)
            configfile = configfile
        else:
            print 'Using config file from default location'
            configfile = os.environ['HOME'] + '/' + '.kube' + '/' + 'config'
        try:
            print 'Reading kube config file...'
            stream = open(configfile, 'r')
            docs = yaml.load(stream)
            return_tls_certs = {
                'certificate-authority-data': docs['clusters'][0]['cluster']['certificate-authority-data'],
                'client-certificate-data': docs['users'][0]['user']['client-certificate-data'],
                'client-key-data': docs['users'][0]['user']['client-key-data']}
            return return_tls_certs
        except IOError as e:
            print 'issue reading the files {}'.format(e)

    @staticmethod
    def write_file(return_tls_certs, destdir=None):
        '''
        write certs to dest dir
        :param return_tls_certs:
        :param destdir:
        :return:
        '''
        if destdir:
            destdir = destdir
        else:
            destdir = '../ssl'
        print 'Writine tls certs to dest:{}'.format(destdir)
        try:
            f = open(destdir + '/' + 'ca_cert.crt', 'w')
            f.write(base64.b64decode(return_tls_certs['certificate-authority-data']))
        except IOError as e:
            print 'issue writing the files {}'.format(e)
        try:
            g = open(destdir + '/' + 'cert_file.crt', 'w')
            g.write(base64.b64decode(return_tls_certs['client-certificate-data']))
        except IOError as e:
            print 'issue writing the files {}'.format(e)
        try:
            h = open(destdir + '/' + 'key_file.crt', 'w')
            h.write(base64.b64decode(return_tls_certs['client-key-data']))
        except IOError as e:
            print 'issue writing the files {}'.format(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', required=False, type=str, metavar='destdir', help='Dest dir where to write tls files')
    parser.add_argument('--configfile', required=False, type=str, metavar='configfile', help='Kube config file location')
    args = parser.parse_args()
    ssl = SslUtility()
    if args.configfile is None:
        ssl_dict = ssl.read_config()
    else:
        ssl_dict = ssl.read_config(args.configfile)

    if args.dest is None:
        ssl.write_file(ssl_dict)
    else:
        ssl.write_file(ssl_dict, args.dest)
