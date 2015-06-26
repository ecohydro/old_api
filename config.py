import os
from app.HMACAuth import HMACAuth

basedir = os.path.abspath(os.path.dirname(__file__))


def make_mongo_uri(
        host='localhost',
        port=27017,
        database='default',
        replica_set=None,
        username=None,
        password=None):
    uri = 'mongodb://'
    if username is not None and password is not None:
        uri += username + ':' + password + '@'
    if ',' in host:
        host = host.split(',')
    if not isinstance(host, basestring):
        if port is not None:
            host = [x + ':' + str(port) for x in host]
        uri += ",".join(host)
    else:
        uri += host
        if port is not None:
            uri += ':' + str(port)
    if database is not None:
        uri += '/' + database
    if replica_set is not None:
        uri += '?replicaSet=' + replica_set
    return uri


class Config:
    def __init__(self):
        self.eve_settings = {
            'PUBLIC_METHODS': ['GET'],
            'PUBLIC_ITEM_METHODS': ['GET'],
            'DOMAIN': {'stub': {}},
            'LAST_UPDATED': 'updated',
            'DATE_CREATED': 'created'
        }
    PAGINATION_DEFAULT = 200
    PAGINATION_LIMIT = 400
    auth = HMACAuth
    API_NAME = 'PulsePod API, Version 1.0'
    PREFERRED_URL_SCHEME = 'https'
    # APP SECRET KEYS:
    SECRET_KEY = os.environ.get('APP_SECRET')
    GATEWAY_SECRET = os.environ.get('GATEWAY_SECRET')
    # Set Tokens and Auth:
    HIREFIRE_TOKEN = os.environ.get('HIREFIRE_TOKEN')
    API_AUTH_TOKEN = os.environ.get('API_AUTH_TOKEN')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    # BITLY CONFIG:
    BITLY_API_TOKEN = os.environ.get('BITLY_API_TOKEN')
    BITLY_API_KEY = os.environ.get('BITLY_API_KEY')
    BITLY_USERNAME = os.environ.get('BITLY_USERNAME')
    # AWS CONFIG:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET = os.environ.get('AWS_BUCKET')
    # MAILGUN INFORMATION
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    # MAIL INFORMATION
    PULSEPOD_MAIL_SENDER = 'PulsePod Admin <postmaster@pulsepod.io>'
    PULSEPOD_MAIL_SUBJECT_PREFIX = '[PulsePod] '
    PULSEPOD_ADMIN = os.environ.get('PULSEPOD_ADMIN')
    REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    # TWILIO CONFIG
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_URL = 'https://api.twilio.com/2010-04-01/Accounts/'
    TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
    # EARTH ENGINE CONFIG
    EE_CLIENT_ID = os.getenv('EE_CLIENT_ID')
    EE_CREDENTIALS = {
        "refresh_token":
        "1/Xn-HgT-pQbxPowGgsL164v3YXzs-id9EpUoHYgOVj3wMEudVrK5jSpoR30zcRFq6"
    }
    # STRIPE CONFIG:
    STRIPE_API_KEY = os.getenv('STRIPE_DEV_API_KEY')
    # Server config settings:
    FORM = 'application/x-www-form-urlencoded; charset=UTF-8'
    JSON = 'application/json'
    # Set defaults:
    LOCATION = {'lat': 40.3501479, 'lng': -74.6516628, 'accuracy': 100}
    ELEVATION = {'elevation': 30, 'resolution': 1}
    XLSX_PATH = 'app/static/xlsx/'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    def __init__(self):
        Config.__init__(self)
        # self.eve_settings['MONGO_DBNAME'] =
        #    os.environ.get('MONGO_DEV_DBNAME')
        # self.eve_settings['MONGO_HOST'] = os.environ.get('MONGO_DEV_HOST')
        # self.eve_settings['MONGO_PASSWORD'] = os.environ.get(
        #     'MONGO_DEV_PASSWORD')
        # self.eve_settings['MONGO_PORT'] = int(os.environ.get(
        #     'MONGO_DEV_PORT'))
        # self.eve_settings['MONGO_USERNAME'] = os.environ.get(
        #     'MONGO_DEV_USERNAME')
        self.eve_settings['MONGO_URI'] = make_mongo_uri(
            host=os.environ.get('MONGO_DEV_HOST'),
            port=int(os.environ.get('MONGO_DEV_PORT')),
            database=os.environ.get('MONGO_DEV_DBNAME'),
            username=os.environ.get('MONGO_DEV_USERNAME'),
            password=os.environ.get('MONGO_DEV_PASSWORD'),
        )
    ASSETS_DEBUG = True
    DEBUG = True
    SERVER_NAME = '0.0.0.0:5000'
    API_URL = 'http://' + SERVER_NAME
    # TWILIO_POST_URL = API_URL + '/gateway/twilio'
    # This is wrong, but we've set it to get twilio tests to work:
    TWILIO_POST_URL = 'https://gateway.pulsepod.io/twilio'
    # MONGO_DBNAME = os.environ.get('MONGO_DEV_DBNAME')
    # MONGO_HOST = os.environ.get('MONGO_DEV_HOST')
    # MONGO_PASSWORD = os.environ.get('MONGO_DEV_PASSWORD')
    # MONGO_PORT = int(os.environ.get('MONGO_DEV_PORT'))
    # MONGO_USERNAME = os.environ.get('MONGO_DEV_USERNAME')
    # PYMONGO_DBNAME = os.environ.get('MONGO_DEV_DBNAME')
    # PYMONGO_HOST = os.environ.get('MONGO_DEV_HOST')
    # PYMONGO_PASSWORD = os.environ.get('MONGO_DEV_PASSWORD')
    # PYMONGO_PORT = int(os.environ.get('MONGO_DEV_PORT'))
    # PYMONGO_USERNAME = os.environ.get('MONGO_DEV_USERNAME')
    PYMONGO_HOST = make_mongo_uri(
        host=os.environ.get('MONGO_DEV_HOST'),
        port=int(os.environ.get('MONGO_DEV_PORT')),
        database=os.environ.get('MONGO_DEV_DBNAME'),
        username=os.environ.get('MONGO_DEV_USERNAME'),
        password=os.environ.get('MONGO_DEV_PASSWORD'),
    )
    MONGODB_SETTINGS = {
        # "DB": os.environ.get('MONGO_DEV_DBNAME'),
        # "USERNAME": os.environ.get('MONGO_DEV_USERNAME'),
        # "PASSWORD": os.environ.get('MONGO_DEV_PASSWORD'),
        # "HOST": os.environ.get('MONGO_DEV_HOST'),
        # "PORT": int(os.environ.get('MONGO_DEV_PORT'))
        "HOST": make_mongo_uri(
            host=os.environ.get('MONGO_DEV_HOST'),
            port=int(os.environ.get('MONGO_DEV_PORT')),
            database=os.environ.get('MONGO_DEV_DBNAME'),
            username=os.environ.get('MONGO_DEV_USERNAME'),
            password=os.environ.get('MONGO_DEV_PASSWORD'),
        )
    }


class TestingConfig(Config):
    def __init__(self):
        Config.__init__(self)
        # self.eve_settings['MONGO_DBNAME'] = 'testing'
        # self.eve_settings['MONGO_HOST'] = 'localhost'
        # self.eve_settings['MONGO_PORT'] = 27107
        self.eve_settings['MONGO_URI'] = make_mongo_uri()
    auth = HMACAuth
    ASSETS_DEBUG = True
    DEBUG = True
    SERVER_NAME = '0.0.0.0:5000'
    API_URL = 'http://' + SERVER_NAME
    # TWILIO_POST_URL = API_URL + '/gateway/twilio'
    # This is wrong, but we've set it to get twilio tests to work:
    TWILIO_POST_URL = 'https://gateway.pulsepod.io/twilio'
    TESTING = True
    MONGO_DBNAME = 'testing'
    MONGO_HOST = 'localhost'
    MONGO_PASSWORD = ''
    MONGO_PORT = 27017
    MONGO_USERNAME = ''
    PYMONGO_DBNAME = 'testing'
    PYMONGO_HOST = 'localhost'
    PYMONGO_PASSWORD = ''
    PYMONGO_PORT = 27017
    PYMONGO_USERNAME = ''
    CLOUDMQTT_URL = 'mqtt://localhost:1883'
    # PYMONGO_HOST = make_mongo_uri()
    MONGODB_SETTINGS = {
        "DB": 'testing',
        "HOST": 'localhost',
        "PORT": 27017
    }


class ProductionConfig(Config):
    def __init__(self):
        Config.__init__(self)
        self.eve_settings['MONGO_URI'] = make_mongo_uri(
            host=os.environ.get('MONGO_HOST'),
            port=None,  # port is defined in MONGO_HOST for replica sets
            database=os.environ.get('MONGO_DBNAME'),
            username=os.environ.get('MONGO_USERNAME'),
            password=os.environ.get('MONGO_PASSWORD'),
            replica_set=os.environ.get('MONGO_REPLICASET')
        )
    SERVER_NAME = 'api.pulsepod.io'
    API_URL = 'https://' + SERVER_NAME
    TWILIO_POST_URL = API_URL + '/gateway/twilio'
    REDISTOGO_URL = os.environ.get('REDISTOGO_URL')
    SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
    CLOUDMQTT_URL = os.environ.get('CLOUDMQTT_URL')
    NEW_RELIC_APP_NAME = 'pulse-api'
    NEW_RELIC_LOG = 'stdout'
    NEW_RELIC_LICENSE_KEY = os.environ.get('NEW_RELIC_LICENSE_KEY')
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME')
    MONGO_HOST = os.environ.get('MONGO_HOST')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    MONGO_REPLICASET = os.environ.get('MONGO_REPLICASET')
    MONGO_URI = make_mongo_uri(
        host=os.environ.get('MONGO_HOST'),
        port=None,  # port is defined in MONGO_HOST for replica sets
        database=os.environ.get('MONGO_DBNAME'),
        username=os.environ.get('MONGO_USERNAME'),
        password=os.environ.get('MONGO_PASSWORD'),
        replica_set=os.environ.get('MONGO_REPLICASET')
    )
    PYMONGO_HOST = make_mongo_uri(
        host=os.environ.get('MONGO_HOST'),
        port=None,  # port is defined in MONGO_HOST for replica sets
        database=os.environ.get('MONGO_DBNAME'),
        username=os.environ.get('MONGO_USERNAME'),
        password=os.environ.get('MONGO_PASSWORD'),
        replica_set=os.environ.get('MONGO_REPLICASET')
    )
    MONGODB_SETTINGS = {
        "HOST": make_mongo_uri(
            host=os.environ.get('MONGO_HOST'),
            port=None,  # port is defined in MONGO_HOST for replica sets
            database=os.environ.get('MONGO_DBNAME'),
            username=os.environ.get('MONGO_USERNAME'),
            password=os.environ.get('MONGO_PASSWORD'),
            replica_set=os.environ.get('MONGO_REPLICASET')
        )
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
