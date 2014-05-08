import requests
from requests.auth import HTTPBasicAuth
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
		self.pod_serial_number_length = 4
		self.type = 'unknown'
		self.frame = self.__class__.__name__
		if data:
			# Stuff that every message should have:
			self.etags = {}
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
			self.pod_data = None
		else:
			assert 0, "Must provide message data to initialize SMS"	

		# New things we will need to determine:
		if self.status == 'posted' and self.type == 'data':
			self.nobs = data['nobs']
			self.nposted = data['nposted']
			self.data_ids = data['data_ids']
		else:
			self.nobs = 0
			self.nposted = 0
			self.data_ids = []
			self.data = None

	def post(self):
		if not self.status == 'invalid':
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
		else:
			pass

	def patch(self): 
		patched={}
		# FIRST PATCH THE MESSAGE CONTENT:
		patched['type'] = self.type	
		patched['frame'] = self.frame
		patched['status'] = self.status 
		# IF WE PARSED SUCCESFULLY....
		if self.status is 'parsed':
			patched['pod'] = self.pod()['_id']
			patched['pod_name'] = self.pod()['name']
		else: # OR NOT
			patched['pod'] = None
			patched['pod_name'] = None
		# IF THIS IS A DATA MESSAGE.....
		if self.type is 'data':
			patched['nobs'] = self.nobs
			if self.nposted > 0: 
				patched['status'] = 'posted'
				patched['nposted'] = self.nposted
				patched['data'] = self.data_ids
				patched['notebook'] = self.pod()['notebook']
				status={}
				v = next((item for item in self.data if item["sensor"] == "525ebfa0f84a085391000495"), None)
				# But we need to extract the vbatt_tellit out of the data blob. 
				# Use the Sensor Id, which should be relatively constant. HACKY! 
				if v:
					status['last'] = v['t']
					status['voltage'] = v['v']
					status['status'] = 'active'
				if not self.number == self.pod()['number']:
					status['number'] = self.number 
				if patch:
					# Don't forget to set the content type, because it defaults to html			
					headers= {'If-Match':str(self.stat_etag()),'content-type':'application/json'}
					auth = HTTPBasicAuth('api',HMACAuth().compute_signature(url,data))
					u = requests.patch(url=self.stat_url(),data=json.dumps(status),headers=headers,auth=auth)
					# Need to have some graceful failures here... Response Code? HACKY!
		# PATCH THE MESSAGE...		
		try:
			# SHOULD THIS BE DONE WITH PYMONGO?
			data = json.dumps(patched)
			url = self.url
			headers = { 'If-Match' : str( self.msg_etag() ), 'content-type' : 'application/json' }
			auth = HTTPBasicAuth('api', HMACAuth().compute_signature( url , data ))
			p = requests.patch( url = url, data = data, headers = headers, auth = auth)
			response = {}
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
		except:
			assert 'Error sending patch request to server'
		
	def parse(self):
		"""
    	go through the user data of the message
    	| sid | nObs | unixtime1 | value1 | unixtime2 | value2 | ... | valueN |
    	sid = 1byte
    	nObs = 1byte
    	unixtime = 4 bytes LITTLE ENDIAN
    	value = look up length
    	"""  	
		i = 2 + self.pod_serial_number_length
		self.status = 'parsed'
		self.data=[]
		self.nobs=0 # Initialize observation counter
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
			self.nobs += nobs
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
							  'notebook': self.pod()['_current_notebook'],
							  'loc':{
							  		'type':'Point',
							  		'coordinates':[self.lng(), self.lat()]
							  },
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
		
	# Pod and Notebook Identity Functions:
			
	def pod(self): # Get the pod document for this message
		if not self.pod_data: # and self.etags['pod'] == self.pod_etag():
			self.pod_data = self.db['pods'].find_one({'pod_id':self.pod_id()})
		return self.pod_data 

	def notebook(self):
		return self.db['pods_notebooks'].find_one({'_id_pod':self.pod()['_id'],'_notebook':self.pod()['_notebook']})
	
	def stat_url(self):
		return str(self.config['API_URL'] + '/pods/status/' + str(self.pod()['name']))

	def pod_url(self):
		return self.config['API_URL'] + '/pods/' + str(self.pod()['_id'])

	# Pod and Notebook Ids:
	def pod_id(self):
		try:
			pod_id =  int(self.content[2:2+self.pod_serial_number_length], 16)	
		except ValueError:
			self.status = 'invalid'
			assert 0, "Invalid Message: " + self.content
		return pod_id

	# Return Message Etag:
	def msg_etag(self): # Return this message's etag
		return str(requests.head(self.url).headers['Etag'])

	def stat_etag(self):
		return str(requests.head(self.stat_url()).headers['Etag'])

	def pod_etag(self):
		return str(requests.head(self.pod_url()).headers['Etag'])

	def lat(self):
		return self.notebook()['location']['lat']

	def lng(self):
		return self.notebook()['location']['lng']







