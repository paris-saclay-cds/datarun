import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'blabla-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    os.environ['DIR_DATA'] = 'raw_data/'
    os.environ['DIR_SUBMISSION'] = 'submission_directory/'


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL_TEST']
    os.environ['DIR_DATA'] = 'test_data/'
    os.environ['DIR_SUBMISSION'] = 'test_submission/'
