import logging
import os
import time

if not os.path.exists('logs'):
    try:
        print 'logs dir is not present, it will be created on the fly'
        os.makedirs('logs')
    except IOError as e:
        print 'problems creating the dir logs: {0}'.format(e)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


fh = logging.FileHandler('logs/logs-{0}.log'.format(time.strftime("%Y%m%d-%H%M%S")))
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)
