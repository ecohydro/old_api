import os, sys
import time
import requests
import json
import random
import hashlib
from datetime import datetime
from eve import Eve
from flask import jsonify, request
from eve.utils import config

from pulsepod.utils import cfg
from pulsepod.methods.posts import post_data_to_API
from pulsepod.utils.utils import *

# Create an rq queue from rq and worker.py:
import redis
from rq import Queue
from worker import conn

# Set up the worker queues:
post_q = Queue(connection=conn)	 	# This is the queue for parse/post jobs

# We've defined a ONHEROKU variable to determine if we are, well, on Heroku. 
if os.environ.get('ONHEROKU'):
	host = '0.0.0.0'
	port = int(os.environ.get('PORT'))
	debug = False # Don't debug on Heroku.
	settings = '/app/settings.py'
else:
	host = '0.0.0.0'
	port = 5000 
	debug = True
	settings = '../settings.py'

app = Eve(settings=settings)

# Error handling with json output:
@app.errorhandler(InvalidMessage)
def handle_invalid_message(error):
	response = jsonify(error.to_dict())
	response.status_code = error.status_code
	return response

# app.on_pre_POST_<resource> functions
# These functions prepare the document for posting
def before_post(resource, request):
	print 'Post to ' + resource + ' recieved'

def before_post_notebook(resource, request):
	print 'Recieved request to create notebook'
	
def before_patch_notebook(resource, request):
	print 'Recieved request to patch notebook'	
# SMSSync:
""" 
SMSSync uses the Ushahidi-developed SMS forwarding app for android

12/17/13 - The app send json data

We parse the data and reassign variables to match the schema for messages
in our MongoDb database. 

Note: For convenience, we are using the gateway time as the posting time for these messages
"""
def before_post_smssync(request):
	print "Posting smssync JSON entry"

# Twilio
""" 
Twilio gateway. Will be used for all US pods and any other pods that can 
communicate to a local twilio phone number. 

We post the message immediately and pass the message ID to a redis queue (RQ) that then
processes the message and posts the data to the API in the bkgnd. This avoids response timeouts
because the message is inserted (and response generated) quickly, while still allowing
us to parse the message and post the data at a slower pace. Message status is monitored, 
but RQ job status is not. 
"""
def before_post_twilio(request):
	print "Posting twilio JSON entry"

def before_post_nexmo(request):
	print "Posting nexmo JSON entry"

#### BEFORE INSERT METHODS
def before_insert_pod(documents):
	for d in documents:
		print "Adding " + d["name"] + " to the database"

def before_insert_data(documents):
	print "A POST to data was just performed!"
	for d in documents:
		print "Posting " + d["s"] + " data from " + d["p"] + " to the database"

def before_insert_notebook(documents):
	for d in documents:
		print "Adding " + d["name"] + " notebook to the database"

def before_insert_smssync(documents):
	print "Adding SMSSync SMS to messages database"

def before_insert_twilio(documents):
	print "Adding Twilio SMS to messages database"

def before_insert_nexmo(documents):
	print "Adding Nexmo SMS to messages database"

# app.on_post_POST functions:	
# These functions prepare gateway-specific responses to the client 
def post_smssync_return_callback(request, r):
	pass

def post_twilio_return_callback(request, r):
	pass

def post_nexmo_return_callback(request,r):
	pass

# Do this one last...`
def post_return_callback(res,request,r):
	# Check to make sure we're not dealing with form data from twilio or nexmo:
	# If it's JSON, then we're ready to parse this message
	if (res in ['twilio','smssync','nexmo']):
		print "Queueing " + res + " message for parsing and posting to the API"
		sys.stdout.flush()
		resp = json.loads(r.get_data())
		if not (resp[cfg.STATUS] == cfg.ERR):
			print "Starting worker process"
			post_job = post_q.enqueue(post_data_to_API,str(resp['_id']),res)
		else:
			raise InvalidMessage('Data not sent to API',status_code=400,payload=resp)

# We're running inside of gunicorn now, so we have to change the module name:
if __name__ == 'api':

#	app.on_post_POST_nexmo += post_nexmo_return_callback
	app.on_post_POST += post_return_callback
# Start the application
# if __name__ == 'api':
# Adding data to the system:
	app.on_insert_data += before_insert_data

# Administering pods, gateways, and sensors:
# Run the program:
#	app.run(host=host, port=port, debug=debug)
