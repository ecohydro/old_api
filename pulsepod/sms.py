import requests
import hashlib
import json

from pulsepod.utils import cfg
from pulsepod.utils.utils import InvalidMessage
from pulsepod.utils.utils import get_sensor, get_time, get_value
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
			self.data = []
	
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
		self.update_notebook() # update notebook for data messages

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
		while i < self.len():
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

	def update_notebook():
		v = next((item for item in self.data if item["sensor"] == "525ebfa0f84a085391000495"), None)
		# But we need to extract the vbatt_tellit out of the data blob. 
		# Use the Sensor Id, which should be relatively constant. HACKY! 
		if v:
			nbk_update={}
			nbk_update["last"] = v["t"]
			nbk_update["voltage"] = v["v"]
			# Don't forget to set the content type, because it defaults to html
			this_notebook = cfg.API_URL + "/notebooks/" + str(self.nbkId())				
			headers= {'If-Match':str(self.notebook()['_etag']),'content-type':'application/json'}
			u = requests.patch(this_notebook,data=json.dumps(nbk_update),headers=headers)
			# Need to have some graceful failures here... Response Code? HACKY!
			return u.status_code
		else: 
			return None	

	def pod(self): # Get the pod document for this message
		if self.pod_data == None or not self.pod_data['_etag'] == requests.head(self.podurl()).headers['Etag']:
			self.pod_data = requests.get(self.podurl()).json()
		return self.pod_data

	def notebook(self): # Get the notebook document for this message
		if self.nbk_data == None or not self.nbk_data['_etag'] == requests.head(self.nbkurl()).headers['Etag']:
			self.nbk_data =  requests.get(self.nbkurl()).json()
		return self.nbk_data

	def podurl(self): # Get the pod url for this message
		return str(cfg.API_URL + '/pods/' + self.podId())

	def nbkurl(self): # Determine the URL to access this message's notebook
		return str(cfg.API_URL + '/notebooks/' + str(self.nbkId()))

	def podId(self):
		self.POD_SERIAL_NUMBER_LENGTH = 4
		podId =  str(hashlib.sha224(str(int(self.content[2:2+POD_SERIAL_NUMBER_LENGTH], 16))).hexdigest()[:10])	
		return podId

	def nbkId(self): # Get the notebook ID for this message by querying the pod
		return self.pod()['notebook']

	def etag(self): # Return this message's etag
		return str(requests.head(self.url).headers['Etag'])

	def type(self):
		return self.__class__.__name__
		
	def len(self):
		return len(self.content)

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


class deploy(SMS):
	
	def nbkurl(self):
		pass

	def parse(self):
		print "parsing deploy message"
		# Deployment message
		# Length = 2 + 20 + 2 + 2*n_sensors = 24 + 2*n_sensors
		##############################################################
		#Var:  |FrameId|PodId|MCC|MNC|LAC|CI|n_sensors|sID1| ... |sIDn|
		#len:  |  2    | 4   | 3 | 3 | 4 | 8| 1    	  | 2  | ... | 2  |
		##############################################################
		json=[]
		i=2+self.pod_serial_number_length()
		min_length = 2 + self.pod_serial_number_length() + 3 + 3 + 4 + 8 + 1

		# make sure message is long enough to read everything
		payload = {'_id':self._id,'type':self.type(),'content':self.content}
		
		# Need to get geolocation data
		# Need to format notebook for this pod
		if len(self.content) < min_length:
			raise InvalidMessage('Status message too short', status_code=400, payload=payload)
		mcc = int(self.content[i:i+3], 16)
		i +=3
		mnc = int(self.content[i:i+3], 16)
		i += 3
		lac = int(self.content[i:i+4], 16)
		i += 4
		cell_id = int(self.content[i:i+8], 16)
		i += 8
		n_sensors = int(self.content[i:i+1], 16)
		i += 1
		# now make sure length is actually correct
		if len(self.content) != (25 + 2*n_sensors):
			raise InvalidMessage('Status message improperly formatted', status_code=400, payload=payload)
		# sIDs is list of sensor objectIds
		sids = []
		s_ids = []
		for j in range(n_sensors):
			this_url = cfg.API_URL + '/sensors/' + str(int(self.content[i:i+2], 16))
			print this_url
			s = requests.get(this_url).json()
			sids.append(s['sid'])
			s_ids.append(s['_id'])
			i += 2

		self.data = {
			'cellTowers': {
				'locationAreaCode': lac, 
				'cellId': cell_id, 
				'mobileNetworkCode': mnc,
				'mobileCountryCode': mcc
			},
			'sensors': s_ids,
			'sids': sids,
		}
		
		self.data['location'] = google_geolocate_api(self.data['cellTowers'])
		self.data['elevation'] = google_elevation_api(self.data['location'])
		self.data['address'] = google_geocoding_api(self.data['location'])		
		self.data['name'] = self.pod()['name'] + 'data from' + \
							self.data['address']['locality'] + \
						    'in' self.data['address']['country']

	def post(self):
		print "posting deploy message"
		# Need to create new notebook 
		print "creating new notebook"
		nbkurl = cfg.API_URL + '/notebooks'
		headers = {'content-type':'application/json'}
		print self.data
		d = requests.post(url=nbkurl, data=json.dumps(self.data), headers=headers)
		if d.status_code == cfg.CREATED:
			pod_update={}
			item = d.json()
			print 'Item status: ' + item[cfg.STATUS]
		 	if not item[cfg.STATUS] == cfg.ERR:
		 		# PATCH THE POD ASAP:
		 		pod_update['notebook'] = item[u'_id']
		 		headers= {'If-Match':str(self.pod()['_etag']),'content-type':'application/json'}
		 		p = requests.patch(self.podurl(),data=json.dumps(pod_update),headers=headers)
		else:
			print d.status_code
			print d.text
		

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
		patched['status'] = self.status
		self.patch_message(patched)




