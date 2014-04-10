import requests
import hashlib
import json
import datetime

from pulsepod.utils import cfg
from pulsepod.utils.utils import InvalidMessage
from pulsepod.utils.utils import get_sensor, get_time, get_value, get_now
from pulsepod.utils.utils import google_geolocate_api, google_elevation_api, google_geocoding_api

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
			self.url = cfg.API_URL + self.href
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
			data = requests.get(url).json()
		if data == None:
			assert 0, "Must provide a url or message data"

		# Do a bunch of stuff to determine type:
		# (3) Read message type from message content
		type = cfg.FRAMES[int(data['message'][0:2],16)]
		if type == "number": 	return number(data)
		if type == "imei": 		return podId(data)
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
		dataurl = cfg.API_URL + '/data'
		headers = {'content-type':'application/json'}
		d = requests.post(url=dataurl, data=json.dumps(self.data), headers=headers)
		if d.status_code == cfg.CREATED:
			items = d.json()
		 	for item in items:
		 		print 'Item status: ' + item[cfg.STATUS]
		 		if not item[cfg.STATUS] == cfg.ERR:
		 			nposted = nposted + 1
		 			self.data_ids.append(item[u'_id'])
		else:
			print json.dumps(d.json())
			# print 'POST:[' + str(d.status_code) + ']:' + d.json()[cfg.STATUS] + ':' + json.dumps(d.json()['_issues'])
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
		self.patch_notebook() # update notebook for data messages
		self.patch_pod() 	  # update the pod if number has changed


	def patch_message(self,patched):
		# Patch the message
		response = {}
		headers = {'If-Match':str(self.etag()),'content-type':'application/json'}
		p = requests.patch(self.url,data=json.dumps(patched),headers=headers)
		if p.status_code == requests.codes.ok:
			response['status'] = patched['status'] 	# RQ reporting
			response['patch code'] = p.status_code 	# RQ reporting
			if p.json()[cfg.STATUS] == cfg.ERR:
				print 'PATCH:[' + str(response['patch code']) + ']:' + p.json()[cfg.STATUS] + ':' + json.dumps(p.json()[cfg.ISSUES])
			else:		   
				print 'PATCH:[' + str(response['patch code']) + ']:' + p.json()[cfg.STATUS] + ':' + str(self.url) + ':status:' + str(self.status)
		else:
			print "That shit didn't work"
		return response

	def parse_message(self,i=2):
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
				raise InvalidMessage('Error reading sid',status_code=400)

			sensor = get_sensor(sid) # Retrieve sensor information from API
			i += 2
			nobs = int(self.content[i:i+2], 16) # Read nObs from message content
			i += 2
			total_obs = total_obs + nobs
			if sensor['context'] == '':
				sensor_string = str(sensor['variable'])
			else:
				sensor_string = str(sensor['context']) + ' ' + str(sensor['variable'])
			
			print "s:" + str(sensor_string)
			print 'p:' + str(self.pod()['name'])
			print 'sensor:' + sensor['_id']
			print 'pod:' + self.pod()['_id']
			print 'notebook:' + self.nbkId()

			# add entry for each observation (nObs) by the same sensor
			entry = {}
			while nobs > 0:
				try:
					entry = {
							  's': sensor_string, 
							  'p': str(self.pod()['name']),
							  'sensor': sensor['_id'],
							  'pod': self.pod()['_id'],
							  'notebook': self.nbkId()
							}
				except:
					raise InvalidMessage('Error creating data record', status_code=400, payload=self.pod())
			
				entry['t'] = get_time(self.content,i) # Get the timestamp 
				i += 8

				entry['v'] = get_value(self.content,i,sensor) # Read the value			
				i += 2*sensor['value_length']
							
				# add to big ole json thing
				self.data.append(entry)
				
				nobs -= 1
		self.nobs = total_obs
		self.status = 'parsed'

	# Update function for notebooks (updates voltage, last)
	def patch_notebook(self):
		v = next((item for item in self.data if item["sensor"] == "525ebfa0f84a085391000495"), None)
		# But we need to extract the vbatt_tellit out of the data blob. 
		# Use the Sensor Id, which should be relatively constant. HACKY! 
		if v:
			nbk_update={}
			nbk_update['last'] = v['t']
			nbk_update['voltage'] = v['v']
			nbh_update['status'] = 'active'
			# Don't forget to set the content type, because it defaults to html			
			headers= {'If-Match':str(self.notebook()['_etag']),'content-type':'application/json'}
			u = requests.patch(self.nbkurl(),data=json.dumps(nbk_update),headers=headers)
			# Need to have some graceful failures here... Response Code? HACKY!
			return u.status_code
		else: 
			return None	

	# Update function for pods (updates pod number if SIM has changed)
	def patch_pod(self):
		if not self.number == self.pod()['number']:
			pod_update={}
			pod_update['number'] = self.number
			headers= {'If-Match':str(self.pod()['_etag']),'content-type':'application/json'}
			u = requests.patch(self.podurl(),data=json.dumps(pod_update),headers=headers)
			return u.status_code
		else:
			return None

	# Pod and Notebook Identity Functions:
	def pod(self): # Get the pod document for this message
		if self.pod_data == None or not self.pod_data['_etag'] == requests.head(self.podurl()).headers['Etag']:
			print "Updating pod information for concurrency...."
			self.pod_data = requests.get(self.podurl()).json()
		return self.pod_data

	def notebook(self): # Get the notebook document for this message
		if self.nbk_data == None or not self.nbk_data['_etag'] == requests.head(self.nbkurl()).headers['Etag']:
			self.nbk_data =  requests.get(self.nbkurl()).json()
		return self.nbk_data

	# Pod and Notebook URLs:
	def podurl(self): # Get the pod url for this message
		return str(cfg.API_URL + '/pods/' + self.podId())

	def podurl_objid(self):
		return str(cfg.API_URL + '/pods/' + self.pod()['_id'])

	def nbkurl(self): # Determine the URL to access this message's notebook
		return str(cfg.API_URL + '/notebooks/' + str(self.nbkId()))

	# Pod and Notebook Ids:
	def podId(self):
		podId =  str(hashlib.sha224(str(int(self.content[2:2+self.pod_serial_number_length()], 16))).hexdigest()[:10])	
		return podId

	def nbkId(self): # Get the notebook ID for this message by querying the pod
		return self.pod()['notebook']

	# Return Message Etag:
	def etag(self): # Return this message's etag
		return str(requests.head(self.url).headers['Etag'])

	# Return Message Type (corresponds to SMS subclass name)
	def type(self):
		return self.__class__.__name__

# SUB CLASSES (ONE FOR EACH FRAME TYPE)
class number(SMS): 

	def pod_serial_number_length(self):
		return 0

	def podId(self):
		if self.podIdvalue == None:
			podurl = cfg.API_URL + '/pods/?where={"' + 'number' + '":"' + self.number + '"}'
			self.podIdvalue = str(requests.get(podurl).json()['_items'][0]['podId'])
		return self.podIdvalue

	def post(self):
		self.post_data()

	def parse(self):
		self.parse_message(i=2)

class podId(SMS):
	
	def post(self):
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
		self.patch_pod() 	  # update the pod if number has changed



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
		self.data={}
		print "parsing deploy message"

		payload = {'_id':self._id,'type':self.type(),'content':self.content}
		
		# now make sure length is actually correct
		i=28
		print self.n_sensors()

		if len(self.content) != (i + 2*self.n_sensors()):
			raise InvalidMessage('Status message improperly formatted', status_code=400, payload=payload)
		# sIDs is list of sensor objectIds
		self.data['sids'] = []
		self.data['sensors'] = []
		for j in range(self.n_sensors()):
			this_url = cfg.API_URL + '/sensors/' + str(int(self.content[i:i+2], 16))
			print this_url
			s = requests.get(this_url).json()
			self.data['sids'].append(s['sid'])
			self.data['sensors'].append(s['_id'])
			i += 2

		self.data['cellTowers'] = {
			'locationAreaCode': self.lac(), 
			'cellId': self.cell_id(), 
			'mobileNetworkCode': self.mnc(),
			'mobileCountryCode': self.mcc()
		}
		
		# Set new notebook Id:
		self.data['nbkId'] = self.nbkId()
		# Transfer ownership of pod to notebook:
		self.data['owner'] = self.pod()['owner']	# Owner is always a single user
		self.data['shared'] = [self.pod()['owner']] # Shared is a list of users
		self.data['last'] = get_now()
		self.data['voltage'] = self.voltage()
		self.data['location'] = google_geolocate_api(self.data['cellTowers'])
		self.data['elevation'] = google_elevation_api(self.data['location'])
		self.data['address'] = google_geocoding_api(self.data['location'])		
		self.data['name'] = self.pod()['name'] + ' data from ' + \
							self.data['address']['locality']['short'] + ', ' + \
							self.data['address']['administrative_area_level_1']['short'] + \
						    ' in ' + self.data['address']['country']['short']

	def post(self):
		print "posting deploy message"
		# Need to create new notebook 
		nbkurl = cfg.API_URL + '/notebooks'
		headers = {'content-type':'application/json'}
		print self.data
		d = requests.post(url=nbkurl, data=json.dumps(self.data), headers=headers)
		print self.type() + " deployment status_code: " +  str(d.status_code)
		if d.status_code == cfg.CREATED:
			pod_update={}
			item = d.json()
			print 'Item status: ' + item[cfg.STATUS]
			print 'Item returned' + json.dumps(item)
		 	if not item[cfg.STATUS] == cfg.ERR:
		 		# PATCH THE POD ASAP:
		 		print "Patching " + self.pod()['name'] + " with notebook " + item[u'_id']
		 		pod_update['notebook'] = item[u'_id']
		 		print self.pod()['_etag']
		 		print self.podurl()
		 		headers= {'If-Match':str(self.pod()['_etag']),'content-type':'application/json'}
		 		p = requests.patch(self.podurl_objid(),data=json.dumps(pod_update),headers=headers)
		 		if not p.json()['_status'] == cfg.OK:
			 		print "Pod patch successful"
		 			print p.json()
		else:
			print d.status_code
			print d.text
		

	def patch(self):
		patched={}
		patched['type'] = self.type()	# Update the gateway message type
		patched['status'] = self.status
		self.patch_message(patched)
		self.patch_pod() 	  # update the pod if number has changed


class invalid(SMS):
	def parse(self):
		pass
	def post(self):
		pass
	def patch(self):
		patched={}
		patched['type'] = self.type()	# Update the gateway message type
		patched['status'] = self.status
		self.patch_message(patched)




