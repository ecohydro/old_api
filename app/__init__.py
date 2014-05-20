import os
import json
from eve import Eve
from flask import jsonify
from posts import post_data_to_API, post_pod_create_qr
from HMACAuth import HMACAuth
from utils import InvalidMessageException


# Create an rq queue from rq and worker.py:
from rq import Queue
from worker import conn

# Set up the worker queues:
post_q = Queue(connection=conn)  # This is the queue for parse/post jobs

if os.getenv('ONHEROKU'):
    settings = 'settings.py'
elif os.getenv('ONCODESHIP'):
    # Hating the filesystem,  but nosetests gets lost otherwise
    settings = os.getenv('SETTINGS_FILE', 'settings.py')
else:
    # Hating the filesystem,  but nosetests gets lost otherwise:
    settings = os.getenv('SETTINGS_FILE', 'settings.py')

app = Eve(settings=settings, auth=HMACAuth)

# Create collection objects:
pods = app.extensions['pymongo']['MONGO'][1]['pods']
sensors = app.extensions['pymongo']['MONGO'][1]['sensors']


from app.blueprints.hirefire_blueprint import hirefire_bp as hirefire_module
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
        # print resp
        if not (resp[app.config['STATUS']] == app.config['STATUS_ERR']):
            config = {}
            config['API_URL'] = app.config['API_URL']
            config['BITLY_API_TOKEN'] = app.config['BITLY_API_TOKEN']
            config['AWS_ACCESS_KEY_ID'] = app.config['AWS_ACCESS_KEY_ID']
            config['AWS_SECRET_ACCESS_KEY'] = \
                app.config['AWS_SECRET_ACCESS_KEY']
            # print "starting job..."
            post_q.enqueue(
                post_pod_create_qr,
                str(resp[app.config['ITEM_LOOKUP_FIELD']]),
                config=config)
        else:
            raise InvalidMessageException(
                'Pod not posted to API',
                status_code=400,
                payload=resp)


# Do this one last...
def after_POST_callback(res, request, r):
    print r.status_code
    # Check to make sure we're not dealing with form data from twilio or nexmo:
    # If it's JSON,  then we're ready to parse this message
    if (res in ['twilio', 'smssync', 'nexmo']) and not r.status_code == 401:
        resp = json.loads(r.get_data())
        if not (resp[app.config['STATUS']] == app.config['STATUS_ERR']):
            print "Parsing message posted to " + res
            db = app.extensions['pymongo']['MONGO'][1]
            post_q.enqueue(
                post_data_to_API,
                str(resp[app.config['ITEM_LOOKUP_FIELD']]),
                res,
                config=app.config,
                db=db)
        else:
            raise InvalidMessageException(
                'Data not sent to API',
                status_code=400, payload=resp)

if __name__ == 'app':

    app.on_insert_pods += before_insert_pods
    app.on_post_POST_pods += after_POST_pods_callback
    app.on_post_POST += after_POST_callback
