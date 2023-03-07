# configuration class for flask
import sys


class Config(object):
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    DEBUG = True
    ENV = 'Production'
    sys.tracebacklimit = 1


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'Development'
    TESTING = True
    sys.tracebacklimit = 1


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ENV = 'Testing'
    sys.tracebacklimit = 1
