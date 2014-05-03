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
import qrcode, qrcode.image.svg
from posts import post_data_to_API, post_pod_create_qr
from HMACAuth import HMACAuth
from utils import InvalidMessage
from settings import settings as config

# Create an rq queue from rq and worker.py:
import redis
from rq import Queue
from worker import conn

# Set up the worker queues:
post_q = Queue(connection=conn)	 	# This is the queue for parse/post jobs

app = Eve(settings=config,auth=HMACAuth)

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

def before_post_pods(request):
	pass

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
def before_insert_pods(documents):
	for d in documents:
		print 'Adding ' + d['name'] + ' to the database'
		d['nbk_name'] = str(d['name']) + "'s Default Notebook"
		d['podId'] = make_podId(d['name'])
		d['qr'] = 'https://s3.amazonaws.com/' + app.config['AWS_BUCKET'] \
				  + '/' + str(d['name']) + '.svg'

def before_insert_data(documents):
	print "A POST to data was just performed!"
	for d in documents:
		print "Posting " + d["s"] + " data from " + d["p"] + " to the database"

def before_insert_smssync(documents):
	print "Adding SMSSync SMS to messages database"

def before_insert_twilio(documents):
	print "Adding Twilio SMS to messages database"

def before_insert_nexmo(documents):
	print "Adding Nexmo SMS to messages database"

# app.on_post_POST functions:	
# These functions prepare gateway-specific responses to the client 
def after_POST_pods_callback(request,r):
	resp = json.loads(r.get_data())
	if not (resp[app.config['STATUS']] == app.config['STATUS_ERR']):
	 	qr_job = post_q.enqueue(post_pod_create_qr,str(resp[app.config['ITEM_LOOKUP_FIELD']]))
	else:
	 	raise InvalidMessage('Pod not posted to API',status_code=400,payload=resp)

# Do this one last...`
def after_POST_callback(res,request,r):
	print r.status_code
	# Check to make sure we're not dealing with form data from twilio or nexmo:
	# If it's JSON, then we're ready to parse this message
	if (res in ['twilio','smssync','nexmo']) and not r.status_code == 401:
		resp = json.loads(r.get_data())
		if not (resp[app.config['STATUS']] == app.config['STATUS_ERR']):
			print "Parsing message posted to " + res
			post_job = post_q.enqueue(post_data_to_API,str(resp[app.config['ITEM_LOOKUP_FIELD']]),res)
		else:
			raise InvalidMessage('Data not sent to API',status_code=400,payload=resp)

# We're running inside of gunicorn now, so we have to change the module name:
if __name__ == 'api':

	app.on_pre_POST += before_post
	app.on_pre_POST_pods += before_post_pods
	
	app.on_insert_pods += before_insert_pods
	app.on_insert_data += before_insert_data
	
	app.on_post_POST_pods += after_POST_pods_callback
	app.on_post_POST += after_POST_callback