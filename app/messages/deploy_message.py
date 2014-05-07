from app.messages import Message
import hashlib
from app.utils import get_time, get_value, get_now
from app.utils import google_geolocate_api, google_elevation_api, google_geocoding_api


class DeployMessage(Message):

	def __init__(self,data=None,config=None,db=None):
		super(DeployMessage,self).__init__(data=data,config=config,db=db)
		self.type = 'deploy'
		self.frame = self.__class__.__name__

	# Deployment message format (numbers are str length, so 2 x nBytes)
	# 		2 + 4 + 3 + 3 + 4 + 8 + 3 + 1 = 28		   |
	##############################################################
	#Var:  |FrameId|PodId|MCC|MNC|LAC|CI| V | n_sensors|sID1| ... |sIDn|
	#len:  |  2    | 4   | 3 | 3 | 4 | 8| 3 |    1     | 2  | ... | 2  |
	##############################################################
	# Hard-coded based on Deployment message format:
	def mcc(self):
		if self.content:
			try:
				return int(self.content[6:9],16)
			except ValueError as e:
				e.args += ('message content invalid','DeployMessage','mcc()')
				raise
		else:
			self.status='invalid'
			assert 0, "Uh-oh. No message content. You've done something very bad"

	def mnc(self):
		if self.content:
			try:
				return int(self.content[9:12],16)
			except ValueError as e:
				self.status='invalid'
				e.args += ('message content invalid','DeployMessage','mnc()')
				raise
		else:
			self.status='invalid'
			assert 0, "Uh-oh. No message content. You've done something very bad"
	
	def lac(self):
		if self.content:
			try:		
				return int(self.content[12:16],16)
			except ValueError as e:
				e.args += ('message content invalid','DeployMessage','lac()')
				raise
		else:
			self.status='invalid'
			assert 0, "Uh-oh. No message content. You've done something very bad"

	def cell_id(self):
		if self.content:
			try:
				return int(self.content[16:24],16)
			except ValueError as e:
				self.status='invalid'
				e.args += ('message content invalid','DeployMessage','cell_id()')
				raise
		else:
			self.status='invalid'
			assert 0, "Uh-oh. No message content. You've done something very bad"

	def voltage(self):
		if self.content:
			try:
				return int(self.content[24:27],16)
			except ValueError as e:
				self.status='invalid'
				e.args += ('message content invalid','DeployMessage','voltage()')
				raise
		else:
			self.status='invalid'
			assert 0, "Uh-oh. No message content. You've done something very bad"

	def n_sensors(self):
		if self.content:
			try:
				return int(self.content[27:28],16)
			except ValueError as e:
				self.status='invalid'
				e.args += ('message content invalid','DeployMessage','n_sensors()')
				raise
		else:
			self.status='invalid'
			assert 0, "Uh-oh. No message content. You've done something very bad"

	def nbk_id(self):
		if self._created and self.content:
			return str(hashlib.sha224(str(self._created) + str(self.content)).hexdigest()[:10])
		else:
			self.status='invalid'
			assert 0, "Uh-oh. No message nbk_id. You've done something very bad"

	def parse(self):
		# Start by copying pod data to self.data, since PUT is document complete 
		self.data = {}
		self.status='parsed'
		try:
			self.data['name'] = self.pod()['name'] 
			self.data['imei'] = str(self.pod()['imei'])
			self.data['radio'] = self.pod()['radio']
			self.data['pod_id'] = self.pod()['pod_id']
		except KeyError as e:
			e.args += ('pod data missing fields')
			raise

		# now make sure length is actually correct
		i=28
		
		if len(self.content) < i: 
			self.status='invalid'
			assert 0, 'message content length='+ str(len(self.content)) + '. Must be >' +  str(i)  
			return
		elif len(self.content) != (i + 2*self.n_sensors()):
			self.status='invalid'
			assert 0, 'message content length='+ str(len(self.content)) + '. Must equal ' +  str(i + 2*self.n_sensors())
			return

		# sIDs is list of sensor objectIds
		self.data['sids'] = []
		self.data['sensors'] = []
		try:
			for j in range(self.n_sensors()):
				s = self.db['sensors'].find_one({'sid':int(self.content[i:i+2], 16)})
				self.data['sids'].append(s['sid']) # Including to facilitate meteor/mongo array $in queries
				self.data['sensors'].append(s[self.config['ITEM_LOOKUP_FIELD']])
				i += 2
		except:
			self.status='invalid'
			assert 0, 'error reading sensor information from database'
		try:
			self.data['cellTowers'] = {
				'locationAreaCode': self.lac(), 
				'cellId': self.cell_id(), 
				'mobileNetworkCode': self.mnc(),
				'mobileCountryCode': self.mcc()
			}
		except:
			self.status='invalid'
			assert 0, 'error extracting cellular information from message content'
		
		self.data['number'] = self.number
		# Transfer ownership of pod to notebook:
		self.data['owner'] = self.pod()['owner']	# Owner is always a single user
		self.data['shared'] = [self.pod()['owner']] # Shared is a list of users
		self.data['last'] = get_now()
		self.data['voltage'] = self.voltage()
		
		# Do the GOOGLE Stuff:
		location = google_geolocate_api(self.data['cellTowers'],self.config['GOOGLE_API_KEY'])
		self.data['location'] = location if location else self.config['LOCATION']
		elevation = google_elevation_api(self.data['location'],self.config['GOOGLE_API_KEY'])
		self.data['elevation'] = elevation if elevation else self.config['ELEVATION']
		self.data['address'] = google_geocoding_api(self.data['location'],self.config['GOOGLE_API_KEY'])	
		# Make a default pod name based on the location	
		self.data['nbk_name'] = self.pod()['name'] + ' data from ' + \
							self.data['address']['locality']['short'] + ', ' + \
							self.data['address']['administrative_area_level_1']['short'] + \
						    ' in ' + self.data['address']['country']['short']
		
	def post(self):
		if not self.status == 'invalid':
			print "posting deploy message"
			headers = {'If-Match':str(self.pod_etag()),'content-type':'application/json'}
			data = json.dumps(self.data)
			url = self.pod_url
			auth = HTTPBasicAuth('api',HMACAuth().compute_signature(url,data))
			d = requests.put(url=url, data=data, headers=headers, auth=auth)
			if d.status_code == 201:
				print "New deployment created"
			else:
				print d.status_code
				print d.text
		else:
			print "Warning: message format is invalid."

