import requests, sys
import time
import json

from pulsepod.utils import cfg
from pulsepod.sms import SMS

def post_data_to_API(objId,res):
	# Setup the URLs:
	print "Posting data to the API (in post_data_to_API)"
	url = cfg.API_URL + '/messages/' + res + '/' + objId
	message = SMS.create(url=url)
	# Init dicts for message updates and RQ responses:
	response={}
	
	if message.status == 'queued':
		message.parse()
		message.post()
		response = message.patch()
				
	return response



