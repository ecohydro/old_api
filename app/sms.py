import requests
from requests.auth import HTTPBasicAuth
import hashlib
import json
import datetime
from HMACAuth import HMACAuth
from flask import current_app as app
from utils import InvalidMessage
from utils import get_sensor, get_time, get_value, get_now
from utils import google_geolocate_api, google_elevation_api, google_geocoding_api

class SMS(object):
	
	def __init__(self,data=None):
		if data:
			# Stuff that every message should have:
			self._id = data['_id'] if '_id' in data else None
			self.source = data['source'] if 'source' in data else None
			self.status = data['status'] if 'status' in data else  None
			self.content = data['message'] if 'message' in data else None
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
	
	@staticmethod
	def create(data=None, url=None):
		if data == None and url == None:
			assert 0, "Must provide a url or message data"
		if not url == None:
			print url
			data = requests.get(url).json()
		if data == None:
			assert 0, "Must provide a url or message data"

		# Do a bunch of stuff to determine type:
		# (3) Read message type from message content
		try: # Catch invalid messages
			frame_number = int(data['message'][0:2],16)
		except ValueError:
			frame_number = 99
		try: # Catch undefined Frame IDs.
			type = app.config['FRAMES'][frame_number]
		except KeyError:
			type = app.config['FRAMES'][99]
		if type == "number": 	return number(data)
		if type == "podId": 	return podId(data)
		if type == "status": 	return status(data)
		if type == "invalid":	return invalid(data)
		if type == "deploy":	return deploy(data)
		assert 0, "Bad SMS creation: " + type

	def pod_serial_number_length(self):
		return 4

	def post_data(self):
		print "posting data"
		nposted = 0
		dataids = []
		url = app.config['API_URL'] + '/data'
		headers = {'content-type':'application/json'}
		data = json.dumps(self.data)
		auth = HTTPBasicAuth('api',HMACAuth().compute_signature(url,data))
		d = requests.post(url=url, data=data, headers=headers, auth=auth)
		if d.status_code == 201:
			items = d.json()
		 	for item in items:
		 		print 'Item status: ' + item[app.config['STATUS']]
		 		if not item[app.config['STATUS']] == app.config['ERR']:
		 			nposted = nposted + 1
		 			self.data_ids.append(item[u'_id'])
		else:
			print json.dumps(d.json())
			# print 'POST:[' + str(d.status_code) + ']:' + d.json()[app.config['STATUS']] + ':' + json.dumps(d.json()['_issues'])
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
		patched['type'] = self.type()	# Update the gateway message type
		self.patch_message(patched)
		self.patch_status() # update pod with voltages, last, number, etc...

	def patch_message(self,patched):
		# Patch the message
		response = {}
		data = json.dumps(patched)
		url = self.url
		headers = {'If-Match':str(self.msgEtag()),'content-type':'application/json'}
		auth = HTTPBasicAuth('api',HMACAuth().compute_signature(url,data))
		p = requests.patch(url=url,data=data,headers=headers,auth=auth)
		if p.status_code == requests.codes.ok:
			response['status'] = patched['status'] 	# RQ reporting
			response['patch code'] = p.status_code 	# RQ reporting
			if p.json()[app.config['STATUS']] == app.config['ERR']:
				print 'PATCH:[' + str(response['patch code']) + ']:' + p.json()[app.config['STATUS']] + ':' + json.dumps(p.json()[app.config['ISSUES']])
			else:		   
				print 'PATCH:[' + str(response['patch code']) + ']:' + p.json()[app.config['STATUS']] + ':' + str(self.url) + ':status:' + patched['status']
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
		payload = {'_id':self._id,'type':self.type(),'content':self.content}
		while i < len(self.content):
			sensor={} # Reset sensor information
			try:
				sid = int(self.content[i:i+2], 16)
			except:
				self.status='invalid'
			try:
				sensor = get_sensor(sid) # Retrieve sensor information from API
			except:
				raise InvalidMessage('Error contacting API for sensor information', status_code=400, payload=self.pod())
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
					raise InvalidMessage('Error creating data record', status_code=400, payload=self.pod())
				
				try:
					entry['t'] = get_time(self.content,i) # Get the timestamp 
				except:
					self.status='invalid'
				i += 8
				
				try:
					entry['v'] = get_value(self.content,i,sensor) # Read the value			
				except: 
					self.status='invalid'

				i += 2*sensor['value_length']
							
				# add to big ole json thing
				self.data.append(entry)
				
				nobs -= 1
		self.nobs = total_obs
		
	# Pod and Notebook Identity Functions:
	def pod(self): # Get the pod document for this message
		if self.pod_data == None or not self.pod_data[app.config['ETAG']] == requests.head(self.podurl()).headers['Etag']:
			print "Updating pod information for concurrency...."
			self.pod_data = requests.get(self.podurl()).json()
		return self.pod_data

	# Pod and Notebook URLs:
	def podurl(self): # Get the pod url for this message
		return str(app.config['API_URL'] + '/pods/' + self.podId())

	def podurl_objid(self):
		return str(app.config['API_URL'] + '/pods/' + self.pod()[app.config['ITEM_LOOKUP_FIELD']])

	def staturl(self):
		return str(app.config['API_URL'] + '/pods/status/' + str(self.pod()['name']))

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

	# Return Message Type (corresponds to SMS subclass name)
	def type(self):
		return self.__class__.__name__

# SUB CLASSES (ONE FOR EACH FRAME TYPE)
class number(SMS): 

	def pod_serial_number_length(self):
		return 0

	def podId(self):
		if self.podIdvalue == None:
			podurl = app.config['API_URL'] + '/pods/?where={"' + 'number' + '":"' + self.number + '"}'
			self.podIdvalue = str(requests.get(podurl).json()['_items'][0]['podId'])
		return self.podIdvalue

	def post(self):
		if not self.status == 'invalid':
			self.post_data()

	def parse(self):
		self.parse_message(i=2)

class podId(SMS):
	
	def post(self):
		if not self.status == 'invalid':
			self.post_data()

	def parse(self):
		self.parse_message(i=2+self.pod_serial_number_length())
	
class status(SMS):

	def parse(self):
		json = []
		i=2+self.pod_serial_number_length() 
		##################################################################
		# |   LAC  |   CI   | nSensors |  sID1  |  sID1  | ... |  sIDn  |
		# | 2 byte | 8 byte |  1 byte  | 1 byte | 1 byte | ... | 1 byte |
		##################################################################
		# make sure message is long enough to read everything
		
		payload = {'_id':self._id,'type':self.type(),'content':self.content}
		if len(self.content) < 12:
			raise InvalidMessage('Status message too short', status_code=400, payload=payload)
		lac = int(self.content[i:i+4], 16)
		i += 4
		cell_id = int(self.content[i:i+4], 16)
		i += 4
		n_sensors = int(self.content[i:i+2], 16)
		i += 2
		# now make sure length is actually correct
		if len(self.content) != 12 + 2*n_sensors:
			raise InvalidMessage('Status message improperly formatted', status_code=400, payload=payload)

		# sIDs is list of integer sIDs
		sids = []

		for j in range(n_sensors):
			sids.append(int(self.content[i:i+2], 16))
			i += 2

		self.data = {'lac': lac, 'ci': cell_id, 'nSensors': n_sensors, 'sensorlist': sids}
	
	def post(self):
		pass

	def patch(self):
		patched={}
		patched['type'] = self.type()	# Update the gateway message type
		patched['status'] = self.status
		self.patch_message(patched)	
		self.patch_status() 	  # update the pod if number has changed



class deploy(SMS):
	# Deployment message format (numbers are str length, so 2 x nBytes)
	# 		2 + 4 + 3 + 3 + 4 + 8 + 3 + 1 = 28		   |
	##############################################################
	#Var:  |FrameId|PodId|MCC|MNC|LAC|CI| V | n_sensors|sID1| ... |sIDn|
	#len:  |  2    | 4   | 3 | 3 | 4 | 8| 3 |    1     | 2  | ... | 2  |
	##############################################################
	# Hard-coded based on Deployment message format:
	def mcc(self):
		return int(self.content[6:9],16)

	def mnc(self):
		return int(self.content[9:12],16)

	def lac(self):
		return int(self.content[12:16],16)

	def cell_id(self):
		return int(self.content[16:24],16)

	def voltage(self):
		return int(self.content[24:27],16)

	def n_sensors(self):
		return int(self.content[27:28],16)

	def nbkId(self):
		return str(hashlib.sha224(str(self._created) + str(self.content)).hexdigest()[:10])

	def parse(self):
		# Start by copying pod data to self.data, since PUT is document complete 
		self.data = {}
		self.status='parsed'
		try:
			self.data['name'] = self.pod()['name'] 
			self.data['imei'] = self.pod()['imei'] 
			self.data['radio'] = self.pod()['radio']
			self.data['podId'] = self.pod()['podId']
		except:
			self.status='invalid'

		payload = {'_id':self._id,'type':self.type(),'content':self.content}
		
		# now make sure length is actually correct
		i=28
		
		if len(self.content) != (i + 2*self.n_sensors()):
			self.status='invalid'
			raise InvalidMessage('Status message improperly formatted', status_code=400, payload=payload)
		# sIDs is list of sensor objectIds
		self.data['sids'] = []
		self.data['sensors'] = []
		try:
			for j in range(self.n_sensors()):
				sensor_url = app.config['API_URL'] + '/sensors/' + str(int(self.content[i:i+2], 16))
				s = requests.get(sensor_url).json()
				self.data['sids'].append(s['sid'])
				self.data['sensors'].append(s[app.config['ITEM_LOOKUP_FIELD']])
				i += 2
		except:
			self.status='invalid'
		try:
			self.data['cellTowers'] = {
				'locationAreaCode': self.lac(), 
				'cellId': self.cell_id(), 
				'mobileNetworkCode': self.mnc(),
				'mobileCountryCode': self.mcc()
			}
		except:
			self.status='invalid'
		try:
			self.data['number'] = self.number
			# Transfer ownership of pod to notebook:
			self.data['owner'] = self.pod()['owner']	# Owner is always a single user
			self.data['shared'] = [self.pod()['owner']] # Shared is a list of users
			self.data['last'] = get_now()
			self.data['voltage'] = self.voltage()
			self.data['location'] = google_geolocate_api(self.data['cellTowers'])
			self.data['elevation'] = google_elevation_api(self.data['location'])
			self.data['address'] = google_geocoding_api(self.data['location'])		
			self.data['nbk_name'] = self.pod()['name'] + ' data from ' + \
							self.data['address']['locality']['short'] + ', ' + \
							self.data['address']['administrative_area_level_1']['short'] + \
						    ' in ' + self.data['address']['country']['short']
		except:
			self.status='invalid'

	def post(self):
		if not self.status == 'invalid':
			print "posting deploy message"
			# Note, use podurl_objid for PUT requets (podId is read-only!) and send Etag
			headers = {'If-Match':str(self.pod()[app.config['ETAG']]),'content-type':'application/json'}
			data = json.dumps(self.data)
			url = self.podurl_objid()
			auth = HTTPBasicAuth('api',HMACAuth().compute_signature(url,data))
			d = requests.put(url=url, data=data, headers=headers, auth=auth)
			if d.status_code == 201:
				print "New deployment created"
			else:
				print d.status_code
				print d.text
		else:
			print "Warning: message format is invalid."

	def patch(self):
		patched={}
		patched['type'] = self.type()	# Update the gateway message type
		patched['status'] = self.status
		self.patch_message(patched)


class invalid(SMS):
	def parse(self):
		pass
	def post(self):
		pass
	def patch(self):
		patched={}
		patched['type'] = self.type()	# Update the gateway message type
		patched['status'] = 'invalid'
		self.patch_message(patched)




