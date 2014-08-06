import os
from app.HMACAuth import HMACAuth
# from settings import DOMAIN

basedir = os.path.abspath(os.path.dirname(__file__))

# SETTINGS_FILE=/Users/kcaylor/Virtualenvs/api/settings.py
# PYTHONSTARTUP=/Users/kcaylor/Virtualenvs/api/.pystartup
# PULSE_ADMIN=LzKjTo2HieK8SKbZa
# PYTHONUNBUFFERED=true


class Config:
    def __init__(self):
        self.eve_settings = {
            'PUBLIC_METHODS': ['GET'],
            'PUBLIC_ITEM_METHODS': ['GET'],
            'DOMAIN': {'stub': {}}
        }
    auth = HMACAuth
    API_NAME = 'PulsePod API, Version 1.0'
    PREFERRED_URL_SCHEME = 'https'
    # Set Tokens and Auth:
    HIREFIRE_TOKEN = os.environ.get('HIREFIRE_TOKEN')
    API_AUTH_TOKEN = os.environ.get('API_AUTH_TOKEN')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    BITLY_API_TOKEN = os.environ.get('BITLY_API_TOKEN')
    BITLY_API_KEY = os.environ.get('BITLY_API_KEY')
    BITLY_USERNAME = os.environ.get('BITLY_USERNAME')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET = os.environ.get('AWS_BUCKET')
    SECRET_KEY = os.environ.get('APP_SECRET')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    PULSEPOD_MAIL_SENDER = 'PulsePod Admin <postmaster@pulsepod.io>'
    PULSEPOD_MAIL_SUBJECT_PREFIX = '[PulsePod] '
    PULSEPOD_ADMIN = os.environ.get('PULSEPOD_ADMIN')
    REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    APP_URL = os.getenv('http://app.pulsepod.io')
    # Server config settings:
    FORM = 'application/x-www-form-urlencoded; charset=UTF-8'
    JSON = 'application/json'
    LOCATION = {'lat': 40.3501479, 'lng': -74.6516628, 'accuracy': 100}
    ELEVATION = {'elevation': 30, 'resolution': 1}

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    def __init__(self):
        Config.__init__(self)
        self.eve_settings['MONGO_DBNAME'] = os.environ.get('MONGO_DEV_DBNAME')
        self.eve_settings['MONGO_HOST'] = os.environ.get('MONGO_DEV_HOST')
        self.eve_settings['MONGO_PASSWORD'] = os.environ.get('MONGO_DEV_PASSWORD')
        self.eve_settings['MONGO_PORT'] = int(os.environ.get('MONGO_DEV_PORT'))
        self.eve_settings['MONGO_USERNAME'] = os.environ.get('MONGO_DEV_USERNAME')

    ASSETS_DEBUG = True
    DEBUG = True
    # MONGO_DBNAME = os.environ.get('MONGO_DEV_DBNAME')
    # MONGO_HOST = os.environ.get('MONGO_DEV_HOST')
    # MONGO_PASSWORD = os.environ.get('MONGO_DEV_PASSWORD')
    # MONGO_PORT = int(os.environ.get('MONGO_DEV_PORT'))
    # MONGO_USERNAME = os.environ.get('MONGO_DEV_USERNAME')
    PYMONGO_DBNAME = os.environ.get('MONGO_DEV_DBNAME')
    PYMONGO_HOST = os.environ.get('MONGO_DEV_HOST')
    PYMONGO_PASSWORD = os.environ.get('MONGO_DEV_PASSWORD')
    PYMONGO_PORT = int(os.environ.get('MONGO_DEV_PORT'))
    PYMONGO_USERNAME = os.environ.get('MONGO_DEV_USERNAME')
    MONGODB_SETTINGS = {
        "DB": os.environ.get('MONGO_DEV_DBNAME'),
        "USERNAME": os.environ.get('MONGO_DEV_USERNAME'),
        "PASSWORD": os.environ.get('MONGO_DEV_PASSWORD'),
        "HOST": os.environ.get('MONGO_DEV_HOST'),
        "PORT": int(os.environ.get('MONGO_DEV_PORT'))
    }


class TestingConfig(Config):
    def __init__(self):
        Config.__init__(self)
        # self.eve_settings['MONGO_DBNAME'] = 'testing'
        # self.eve_settings['MONGO_HOST'] = 'localhost'
        # self.eve_settings['MONGO_PORT'] = 27107
    auth = None
    ASSETS_DEBUG = True
    DEBUG = True
    API_URL = 'http://0.0.0.0:5000'
    SERVER_NAME = '0.0.0.0:5000'
    TESTING = True
    # MONGO_DBNAME = 'testing'
    # MONGO_HOST = 'localhost'
    # MONGO_PASSWORD = ''
    # MONGO_PORT = 27017
    # MONGO_USERNAME = ''
    PYMONGO_DBNAME = 'testing'
    PYMONGO_HOST = 'localhost'
    PYMONGO_PASSWORD = ''
    PYMONGO_PORT = 27017
    PYMONGO_USERNAME = ''
    MONGODB_SETTINGS = {
        "DB": 'testing',
        "HOST": 'localhost',
        "PORT": 27017
    }


class ProductionConfig(Config):
    def __init__(self):
        Config.__init__(self)
        self.eve_settings['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
        self.eve_settings['MONGO_HOST'] = os.environ.get('MONGO_HOST')
        self.eve_settings['MONGO_PASSWORD'] = os.environ.get('MONGO_PASSWORD')
        self.eve_settings['MONGO_PORT'] = int(os.environ.get('MONGO_PORT'))
        self.eve_settings['MONGO_USERNAME'] = os.environ.get('MONGO_USERNAME')

    API_URL = 'https://api.pulsepod.io'
    SERVER_NAME = 'api.pulsepod.io'
    REDISTOGO_URL = os.environ.get('REDISTOGO_URL')
    NEW_RELIC_APP_NAME = 'pulse-api'
    NEW_RELIC_LOG = 'stdout'
    NEW_RELIC_LICENSE_KEY = os.environ.get('NEW_RELIC_LICENSE_KEY')
    # MONGO_DBNAME = os.environ.get('MONGO_DBNAME')
    # MONGO_HOST = os.environ.get('MONGO_HOST')
    # MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    # MONGO_PORT = int(os.environ.get('MONGO_PORT'))
    # MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    PYMONGO_DBNAME = os.environ.get('MONGO_DBNAME')
    PYMONGO_HOST = os.environ.get('MONGO_HOST')
    PYMONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    PYMONGO_PORT = int(os.environ.get('MONGO_PORT'))
    PYMONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    MONGODB_SETTINGS = {
        "DB": os.environ.get('MONGO_DBNAME'),
        "USERNAME": os.environ.get('MONGO_USERNAME'),
        "PASSWORD": os.environ.get('MONGO_PASSWORD'),
        "HOST": os.environ.get('MONGO_HOST'),
        "PORT": int(os.environ.get('MONGO_PORT'))
    }


class HerokuConfig(ProductionConfig):
    ONHEROKU = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'default': DevelopmentConfig
}
