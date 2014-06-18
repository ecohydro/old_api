import os

basedir = os.path.abspath(os.path.dirname(__file__))

# SETTINGS_FILE=/Users/kcaylor/Virtualenvs/api/settings.py
# PYTHONSTARTUP=/Users/kcaylor/Virtualenvs/api/.pystartup
# PULSE_ADMIN=LzKjTo2HieK8SKbZa
# PYTHONUNBUFFERED=true


class Config:
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

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ASSETS_DEBUG = True
    DEBUG = True
    API_URL = 'http://0.0.0.0:5000/'
    SERVER_NAME = '0.0.0.0:5000'
    MONGO_DBNAME = os.environ.get('MONGO_DEV_DBNAME')
    MONGO_HOST = os.environ.get('MONGO_DEV_HOST')
    MONGO_PASSWORD = os.environ.get('MONGO_DEV_PASSWORD')
    MONGO_PORT = int(os.environ.get('MONGO_DEV_PORT'))
    MONGO_USERNAME = os.environ.get('MONGO_DEV_USERNAME')
    PYMONGO_DBNAME = os.environ.get('MONGO_DEV_DBNAME')
    PYMONGO_HOST = os.environ.get('MONGO_DEV_HOST')
    PYMONGO_PASSWORD = os.environ.get('MONGO_DEV_PASSWORD')
    PYMONGO_PORT = int(os.environ.get('MONGO_DEV_PORT'))
    PYMONGO_USERNAME = os.environ.get('MONGO_DEV_USERNAME')
    # MONGODB_SETTINGS = {
    #     "DB": MONGO_DBNAME,
    #     "USERNAME": MONGO_USERNAME,
    #     "PASSWORD": MONGO_PASSWORD,
    #     "HOST": MONGO_HOST,
    #     "PORT": MONGO_PORT
    # }


class TestingConfig(Config):
    ASSETS_DEBUG = True
    API_URL = 'http://0.0.0.0:5000/'
    SERVER_NAME = '0.0.0.0:5000'
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
    # MONGODB_SETTINGS = {
    #     "DB": MONGO_DBNAME,
    #     "USERNAME": MONGO_USERNAME,
    #     "PASSWORD": MONGO_PASSWORD,
    #     "HOST": MONGO_HOST,
    #     "PORT": MONGO_PORT
    # }


class ProductionConfig(Config):
    API_URL = 'https://api.pulsepod.io'
    SERVER_NAME = 'api.pulsepod.io'
    REDISTOGO_URL = os.environ.get('REDISTOGO_URL')
    NEW_RELIC_APP_NAME = 'pulse-api'
    NEW_RELIC_LOG = 'stdout'
    NEW_RELIC_LICENSE_KEY = os.environ.get('NEW_RELIC_LICENSE_KEY')
    MONGO_DBNAME = os.environ.get('MONGO_DBNAME')
    MONGO_HOST = os.environ.get('MONGO_HOST')
    MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    MONGO_PORT = int(os.environ.get('MONGO_PORT'))
    MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    PYMONGO_DBNAME = os.environ.get('MONGO_DBNAME')
    PYMONGO_HOST = os.environ.get('MONGO_HOST')
    PYMONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
    PYMONGO_PORT = int(os.environ.get('MONGO_PORT'))
    PYMONGO_USERNAME = os.environ.get('MONGO_USERNAME')
    # MONGODB_SETTINGS = {
    #     "DB": MONGO_DBNAME,
    #     "USERNAME": MONGO_USERNAME,
    #     "PASSWORD": MONGO_PASSWORD,
    #     "HOST": MONGO_HOST,
    #     "PORT": MONGO_PORT
    # }


class HerokuConfig(ProductionConfig):
    ONHEROKU = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'default': DevelopmentConfig
}
