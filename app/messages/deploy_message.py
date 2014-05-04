from app.messages import Message

class DeployMessage(Message):

	def __init__(self,data=None,config=None,db=None):
		super(DeployMessage,self).__init__(data=None,config=None,db=None)
		self.type = 'deploy'
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
			raise InvalidMessageException('Status message improperly formatted', status_code=400, payload=payload)
		# sIDs is list of sensor objectIds
		self.data['sids'] = []
		self.data['sensors'] = []
		try:
			for j in range(self.n_sensors()):
				sensor_url = self.config['API_URL'] + '/sensors/' + str(int(self.content[i:i+2], 16))
				s = requests.get(sensor_url).json()
				self.data['sids'].append(s['sid'])
				self.data['sensors'].append(s[self.config['ITEM_LOOKUP_FIELD']])
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
			# Do the GOOGLE Stuff:
			location = google_geolocate_api(self.data['cellTowers'],config['GOOGLE_API_KEY'])
			self.data['location'] = location if location else config['LOCATION']
			elevation = google_elevation_api(self.data['location'],config['GOOGLE_API_KEY'])
			self.data['elevation'] = elevation if elevation else config['ELEVATION']
			self.data['address'] = google_geocoding_api(self.data['location'],config['GOOGLE_API_KEY'])	
			# Make a default pod name based on the location	
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
			headers = {'If-Match':str(self.pod()[self.config['ETAG']]),'content-type':'application/json'}
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