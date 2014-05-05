import requests
from requests.auth import HTTPBasicAuth
import hashlib
import json
import datetime
from app.HMACAuth import HMACAuth

from app.utils import InvalidMessageException
from app.utils import get_time, get_value, get_now
from app.utils import google_geolocate_api, google_elevation_api, google_geocoding_api

class Message(object):
	
	def __init__(self,data=None,config=None,db=None):
		self.config = config if config else None
		self.db = db if db else None
		if data:
			# Stuff that every message should have:
			self.message = data
			self._id = data['_id'] if '_id' in data else None
			self.source = data['source'] if 'source' in data else None
			self.status = data['status'] if 'status' in data else  None
			self.content = str(data['message']) if 'message' in data else None
			self.number = data['number'] if 'number' in data else None
			self.pod_name = data['p'] if 'p' in data else None
			self.href = data['_links']['self']['href'] 
			self._created = data['_created'] if '_created' in data else get_now()
			self.url = 'http://' + self.href
			self.json = data
			self.podIdvalue = None
			self.pod_data = None
			self.nbk_data = None
		else:
			assert 0, "Must provide message data to initialize SMS"	

		# New things we will need to determine:
		if self.status == 'posted':
			self.nobs = data['nobs']
			self.nposted = data['nposted']
			self.data_ids = data['data_ids']
		else:
			self.nobs = 0
			self.nposted = 0
			self.data_ids = []
			self.data = None

	def pod_serial_number_length(self):
		return 4

	def post_data(self):
		print "posting data"
		nposted = 0
		dataids = []
		url = self.config['API_URL'] + '/data'
		headers = {'content-type':'application/json'}
		data = json.dumps(self.data)
		auth = HTTPBasicAuth('api',HMACAuth().compute_signature(url,data))
		d = requests.post(url=url, data=data, headers=headers, auth=auth)
		if d.status_code == 201:
			items = d.json()
		 	for item in items:
		 		print 'Item status: ' + item[self.config['STATUS']]
		 		if not item[self.config['STATUS']] == self.config['STATUS_ERR']:
		 			nposted = nposted + 1
		 			self.data_ids.append(item[u'_id'])
		else:
			print json.dumps(d.json())
			# print 'POST:[' + str(d.status_code) + ']:' + d.json()[self.config['STATUS']] + ':' + json.dumps(d.json()['_issues'])
		self.nposted = nposted

	def patch(self): 
		patched={}
		patched['status'] = self.status 	# Update the gateway message status
		patched['nobs'] = self.nobs			# Update the number of observations in this message
		patched['pod'] = self.pod()['_id']
		patched['p'] = self.pod()['name']
		patched['notebook'] = self.pod()['notebook']
		#print 'message status: ' + patched['status']
		if self.nposted > 0:	# Need to make sure this actually DID post data. Returns 200 with errors.
			patched['status'] = 'posted'	# Update the gateway message status
			patched['nposted'] = self.nposted
			patched['data'] = self.data_ids
		patched['type'] = self.type	# Update the gateway message type
		self.patch_message(patched)
		self.patch_status() # update pod with voltages, last, number, etc...

	def patch_message(self,patched):
		# Patch the message
		patched['type'] = self.type	# Update the gateway message type
		patched['status'] = self.status
		response = {}
		data = json.dumps(patched)
		url = self.url
		headers = {'If-Match':str(self.msgEtag()),'content-type':'application/json'}
		auth = HTTPBasicAuth('api',HMACAuth().compute_signature(url,data))
		p = requests.patch(url=url,data=data,headers=headers,auth=auth)
		if p.status_code == requests.codes.ok:
			response['status'] = patched['status'] 	# RQ reporting
			response['patch code'] = p.status_code 	# RQ reporting
			if p.json()[self.config['STATUS']] == self.config['STATUS_ERR']:
				print 'PATCH:[' + str(response['patch code']) + ']:' + p.json()[self.config['STATUS']] + ':' + json.dumps(p.json()[self.config['ISSUES']])
			else:		   
				print 'PATCH:[' + str(response['patch code']) + ']:' + p.json()[self.config['STATUS']] + ':' + str(self.url) + ':status:' + patched['status']
		else:
			print 'PATCH: [' + str(p.status_code) + ']:' + 'request failed'
		return response

	# Update function for pods (updates voltage, last)
	def patch_status(self):
		patch={}
		if not self.status == 'invalid':
			v = next((item for item in self.data if item["sensor"] == "525ebfa0f84a085391000495"), None)
			# But we need to extract the vbatt_tellit out of the data blob. 
			# Use the Sensor Id, which should be relatively constant. HACKY! 
			if v:
				patch['last'] = v['t']
				patch['voltage'] = v['v']
				patch['status'] = 'active'
			if not self.number == self.pod()['number']:
				patch['number'] = self.number 

		if patch:
			# Don't forget to set the content type, because it defaults to html			
			headers= {'If-Match':str(self.statEtag()),'content-type':'application/json'}
			url = self.staturl()
			data = json.dumps(patch)
			auth = HTTPBasicAuth('api',HMACAuth().compute_signature(url,data))
			u = requests.patch(url=url,data=data,headers=headers,auth=auth)
			# Need to have some graceful failures here... Response Code? HACKY!
			return u.status_code
		else: 
			return None	

	def parse_message(self,i=2):
		self.status = 'parsed'
		self.data=[]
		total_obs=0 # Initialize observation counter
		"""
    	go through the user data of the message
    	| sid | nObs | unixtime1 | value1 | unixtime2 | value2 | ... | valueN |
    	sid = 1byte
    	nObs = 1byte
    	unixtime = 4 bytes LITTLE ENDIAN
    	value = look up length
    	"""    
		payload = {'_id':self._id,'type':self.type,'content':self.content}
		while i < len(self.content):
			try:
				sid = int(self.content[i:i+2], 16)
			except:
				self.status='invalid'
			try:
				sensor = self.db['sensors'].find_one({'sid':sid})
			except:
				raise InvalidMessageException('Error contacting API for sensor information', status_code=400, payload=self.pod())
			i += 2
			try:
				nobs = int(self.content[i:i+2], 16) # Read nObs from message content
			except:
				self.status='invalid'
			i += 2
			total_obs = total_obs + nobs
			try:
				if sensor['context'] == '':
					sensor_string = str(sensor['variable'])
				else:
					sensor_string = str(sensor['context']) + ' ' + str(sensor['variable'])
			except:
				self.status='invalid'

			# add entry for each observation (nObs) by the same sensor
			entry = {}
			while nobs > 0:
				try:
					entry = {
							  's': sensor_string, 
							  'p': str(self.pod()['name']),
							  'sensor': sensor['_id'],
							  'pod': self.pod()['_id'],
							  'notebook': self.pod()['_current_notebook']
							}
				except:
					self.status='invalid'
					raise InvalidMessageException('Error creating data record', status_code=400, payload=self.pod())
				
				try:
					entry['t'] = get_time(self.content,i) # Get the timestamp 
				except:
					self.status='invalid'
				i += 8
				
				try:
					entry['v'] = get_value(self.content,i,sensor) # Read the value			
				except: 
					self.status='invalid'

				i += 2*sensor['nbytes']
							
				# add to big ole json thing
				self.data.append(entry)
				
				nobs -= 1
		self.nobs = total_obs
		
	# Pod and Notebook Identity Functions:
	def pod(self): # Get the pod document for this message
		if self.pod_data == None or not self.pod_data[self.config['ETAG']] == requests.head(self.podurl()).headers['Etag']:
			print "Updating pod information for concurrency...."
			self.pod_data = requests.get(self.podurl()).json()
		return self.pod_data

	# Pod and Notebook URLs:
	def podurl(self): # Get the pod url for this message
		return str(self.config['API_URL'] + '/pods/' + self.podId())

	def podurl_objid(self):
		return str(self.config['API_URL'] + '/pods/' + self.pod()[self.config['ITEM_LOOKUP_FIELD']])

	def staturl(self):
		return str(self.config['API_URL'] + '/pods/status/' + str(self.pod()['name']))

	# Pod and Notebook Ids:
	def podId(self):
		try:
			podId =  str(int(self.content[2:2+self.pod_serial_number_length()], 16))	
		except ValueError:
			self.patch_message({'type':'invalid','status':'invalid'})
			assert 0, "Invalid Message: " + self.content
		return podId

	# Return Message Etag:
	def msgEtag(self): # Return this message's etag
		return str(requests.head(self.url).headers['Etag'])

	def statEtag(self):
		return str(requests.head(self.staturl()).headers['Etag'])










