import requests, sys
import time
import json

from pulsepod.utils import cfg
from pulsepod.SMS import SMS
from pulsepod import frames

""" 
Post data does the following:
1) GETs a specific message from the gateway
2) Checks message status to make sure status is 'queued'
4) Parses the message based on the frame_id
If necessary:
	5) POSTS the parsed data to the API
If status message:
	5) POSTS the pod status to the API
	6) Checks API status code from the pod status posting
7) PATCHes the message on the gateway to indicate the new status (hopefully 'posted')
"""
def post_data_to_API(objID,res):
	# Setup the URLs:
	print "Posting data to the API (in post_data_to_API)"
	message = SMS(objID,res)
	message.url = cfg.MESSAGES_URL + '/' + message.source + '/' + message._id
	# Init dicts for message updates and RQ responses:
	patched={}
	response={}
	# Wait a bit for the database to sort out.
	# time.sleep(1)
	# GET the message information:
	#print 'Mesasage url: ' + message.url

	r = requests.get(message.url)
	if r.status_code == requests.codes.ok:
		message.status = r.json()['status']
	else:
		print '[' + str(r.status_code) + '] ' + ' : ' + message.url + ' not found'
	"""
	 If the message status is 'queued', then we need to:
	 1. parse it
	 2. post it to the API's data/resource if necessary
	 		(will also update the pod voltage if necessary)
	 		(will also update the last date for the pod if necessary) 
	 3. update the message status on the gateway as required
	""" 
	if message.status == 'queued':
		# Define critical message attributes:
		message.content = r.json()['message'] # Extract message content
		message.number = r.json()['pod'] # Determine source pod of message (by number)
		# Specify message methods based on message type
		parse_method = getattr(frames,message.type() + '_parse') # frameID methods based on cfg.FRAMES
		post_method = getattr(frames,message.type() + '_post')   # frameID methods based on cfg.FRAMES
		patch_method = getattr(frames,message.type() + '_patch') # frameID methods based on cfg.FRAMES
		
		message = parse_method(message)	# parse the message.
		message = post_method(message)  # POST the message data to the API
		patched = patch_method(message) # Set PATCH message status and other info for the API
		
		# Patch the message
		headers = {'If-Match':str(r.headers[cfg.ETAG]),'content-type':'application/json'}
		p = requests.patch(message.url,data=json.dumps(patched),headers=headers)
		
		if p.status_code == requests.codes.ok:
			response['status'] = patched['status'] 	# RQ reporting
			response['patch code'] = p.status_code 	# RQ reporting
			if p.json()[cfg.STATUS] == cfg.ERR:
				print 'PATCH:[' + str(response['patch code']) + ']:' + p.json()[cfg.STATUS] + ':' + json.dumps(p.json()[cfg.ISSUES])
			else:		   
				print 'PATCH:[' + str(response['patch code']) + ']:' + p.json()[cfg.STATUS] + ':' + str(message.url) + ':status:' + str(message.status)
		else:
			print "That shit didn't work"


