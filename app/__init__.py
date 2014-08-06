import json
from eve import Eve
from flask import jsonify
from .posts import post_process_message, post_pod_create_qr
from .HMACAuth import HMACAuth
from .utils import InvalidMessageException
from flask.ext.mailgun import Mailgun
from flask.ext.pymongo import PyMongo
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager
from flask.ext.mongoengine import MongoEngine
from eve_mongoengine import EveMongoengine

mail = Mailgun()
pymongo = PyMongo()
db = MongoEngine()
eve_mongo = EveMongoengine()
bootstrap = Bootstrap()
login_manager = LoginManager()

# Create an rq queue from rq and worker.py:
from rq import Queue
from worker import conn

# Set up the worker queues:
post_q = Queue(connection=conn)  # This is the queue for parse/post jobs


def create_app(config_name):

    from config import config
    app = Eve(
        auth=config[config_name]().auth,
        settings=config[config_name]().eve_settings)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize the login manager (for API keys)
    login_manager.init_app(app)

    # Initialize pymongo connection for database migrations
    pymongo.init_app(app, config_prefix='PYMONGO')

    # Initialize bootstrap (for evedocs)
    bootstrap.init_app(app)

    # Initialize MongoEngine (for all the mongo goodness)
    db.init_app(app)

    # Initialize EveMongoEngine (for setting up resources)
    eve_mongo.init_app(app)

    from models.user import User
    eve_mongo.add_model(
        User,
        url='user',
        resource_methods=[],
        item_methods=[]
    )

    from models.data import Data
    eve_mongo.add_model(
        Data,
        url='data',
        resource_methods=['GET'],
        item_methods=['GET'],
        cache_control='max-age=10,must-revalidate',
        cache_expires=10,
        datasource={
            'projection': {
                'nbk': 0,
                'pod': 0,
            }
        }
    )

    from models.sensor import Sensor
    eve_mongo.add_model(
        Sensor,
        url='sensors',
        additional_lookup={
            'url': 'regex("[\w]+")',
            'field': 'sid'
        },
        resource_methods=['GET'],
        item_methods=['GET'],
        cache_control='max-age=20,must-revalidate',
        cache_expires=20,
        datasource={
            'projection': {
                'm': 0,
                'b': 0,
            }
        }
    )

    from models.pod import Pod
    eve_mongo.add_model(
        Pod,
        url='pods',
        additional_lookup={
            'url': 'regex("[\w]+")',
            'field': 'pod_id'
        },
        cache_control='max-age=10,must-revalidate',
        cache_expires=10,
        resource_methods=['GET'],
        item_methods=['GET'],
        datasource={
            'projection': {
                'owner': 0,
            }
        }
    )

    from models.notebook import Notebook
    eve_mongo.add_model(
        Notebook,
        url='notebooks',
        resource_methods=['GET'],
        item_methods=['GET', 'PATCH'],
        datasource={
            'projection': {
                'sensors': 0,
                'pod': 0,
                'owner': 0,
            }
        }
    )

    from models.message import Message, TwilioMessage, PulsePiMessage
    eve_mongo.add_model(
        Message,
        url='messages',
        resource_methods=['GET', 'POST'],
        item_methods=['GET']
    )

    # Spoof messages at twilio and pulsepi (for now):
    eve_mongo.add_model(
        TwilioMessage,
        url='messages/twilio',
        resource_methods=['GET', 'POST'],
        item_methods=['GET']
    )

    eve_mongo.add_model(
        PulsePiMessage,
        url='messages/pulsepi',
        resource_methods=['GET', 'POST'],
        item_methods=['GET']
    )

    # Add API blueprints:
    from eve_docs import eve_docs
    app.register_blueprint(eve_docs, url_prefix='/docs')

    from hirefire import hirefire as hirefire_module
    app.register_blueprint(hirefire_module)

    # Error handling with json output:
    @app.errorhandler(InvalidMessageException)
    def handle_invalid_message(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    # BEFORE INSERT METHODS
    def before_insert_pods(documents):
        for d in documents:
            print 'Adding ' + d['name'] + ' to the database'
            d['nbk_name'] = str(d['name']) + "'s Default Notebook"
            d['qr'] = 'https://s3.amazonaws.com/' + app.config['AWS_BUCKET'] \
                      + '/' + str(d['name']) + '.svg'

    # app.on_post_POST functions:
    # These functions prepare gateway-specific responses to the client
    def after_POST_pods_callback(request, r):
        if r.status_code is 201:
            resp = json.loads(r.get_data())
            if resp[app.config['STATUS']] is not app.config['STATUS_ERR']:
                objId = str(resp[app.config['ITEM_LOOKUP_FIELD']])
                pod = Pod.objects(id=objId).first()
                post_q.enqueue(post_pod_create_qr, pod)
            else:
                raise InvalidMessageException(
                    'Pod not posted to API',
                    status_code=400,
                    payload=resp)

    # Do this one last...
    def after_POST_callback(res, request, r):
        print r.status_code
        # Check to make sure we're not dealing with
        # form data from twilio or nexmo:
        # If it's JSON,  then we're ready to parse this message
        if res in ['message', 'twiliomessage', 'pulsepimessage'] \
                and not r.status_code == 401:
            resp = json.loads(r.get_data())
            if resp[app.config['STATUS']] != app.config['STATUS_ERR']:
                print json.dumps(resp)
                objId = str(resp[app.config['ITEM_LOOKUP_FIELD']])
                if res is 'twiliomessage':
                    message = TwilioMessage.objects(id=objId).first()
                elif res is 'pulsepimessage':
                    message = PulsePiMessage.objects(id=objId).first()
                else:
                    message = Message.objects(id=objId).first()
                # Assign the message frame id:
                print "MessageLog: parsing message from %s" % message.source
                # db = app.extensions['pymongo']['MONGO'][1]
                print "MessageLog: objectId: " + message.get_id()
                print "MessageLog: assigning %s as frame id" % \
                    message.get_frame_id()
                message.frame_id = message.get_frame_id()
                print "MessageLog: assiging %s as message type" % \
                    message.get_type()
                message.message_type = message.get_type()
                message.save()
                post_q.enqueue(post_process_message, message=message)
            else:
                raise InvalidMessageException(
                    'MessageLog: Message not posted to API',
                    status_code=400, payload=resp)

    app.on_insert_pods += before_insert_pods
    app.on_post_POST_pods += after_POST_pods_callback
    app.on_post_POST += after_POST_callback

    return app
