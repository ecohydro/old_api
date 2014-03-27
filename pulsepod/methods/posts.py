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
	#print "Posting data to the API (in post_data_to_API)"
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
		message.content = r.json()['message'] # Extract message content
		message.number = r.json()['pod'] # Determine source pod of message (by number)
		parse_method = getattr(frames,message.type() + '_parse') # frameID methods based on cfg.FRAMES
		post_method = getattr(frames,message.type() + '_post') # frameID methods based on cfg.FRAMES
		message = parse_method(message)	# Parse the message.
		patched['status'] = message.status 	# Update the gateway message status
		patched['nobs'] = message.nobs		# Update the number of observations in this message
		#print 'message status: ' + patched['status']
		message = post_method(message) # POST the message (requires a placeholder method for all frames)
		if message.nposted > 0:	# Need to make sure this actually DID post data. Returns 200 with errors.
			patched['status'] = 'posted'	# Update the gateway message status
			patched['nposted'] = message.nposted
			patched['data_ids'] = message.data_ids
		patched['type'] = message.type()	# Update the gateway message type
		headers = {'If-Match':str(r.headers[cfg.ETAG]),'content-type':'application/json'}
		# Patch the gateway message with the new status and message type
		#print 'patching ' + message.url +' with :' + json.dumps(patched)
		
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


