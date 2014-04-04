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
		update_notebook(message)
	return response

# Data posting utilities
def update_notebook(SMS):
	v = next((item for item in SMS.data if item["sensor"] == "525ebfa0f84a085391000495"), None)
	# But we need to extract the vbatt_tellit out of the data blob. 
	# Use the Sensor Id, which should be relatively constant. HACKY! 
	if v:
		nbk_update={}
		nbk_update["last"] = v["t"]
		nbk_update["voltage"] = v["v"]
		# Don't forget to set the content type, because it defaults to html
		this_notebook = cfg.API_URL + "/notebooks/" + str(SMS.nbkId())				
		headers= {'If-Match':str(SMS.notebook()['_etag']),'content-type':'application/json'}
		u = requests.patch(this_notebook,data=json.dumps(nbk_update),headers=headers)
		# Need to have some graceful failures here... Response Code? HACKY!
		return u.status_code
	else: 
		return None	

	

