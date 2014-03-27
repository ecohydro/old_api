from pulsepod.utils import cfg
from pulsepod.utils.utils import InvalidMessage
import requests

class SMS:
	name = "SMS Message"
	description = "This is a parent class Message"
	def __init__(self,_id=None,source=None,content=None):
		self._id = str(_id) or None
		self.source = str(source) or None
		if not content is None: # The message content must be set
			self.content = content
			self.len = len(self.content)
			self.type = self.type()
			self.frame_id = self.frame_id()

		self.status = 'unknown'
		self.nobs = 0
		self.nposted = 0
		self.data_ids = []

	def frame_id(self):
		if not self.content is None: # Need content to be set
			i=0
			# This function will extract the FrameID (if it exists)
			try:
				frame_id =  int(self.content[i:i+2], 16)
			except: 
				frame_id = 99
			if not frame_id in cfg.FRAMES:
				frame_id = 99
 			return frame_id
 		else:
 			return None

 	def type(self):
 		if not self.content is None: # Needs content to be set
	 		return cfg.FRAMES[self.frame_id()]
	 	else:
	 		return None

	# POD IDs for messages
	def get_pod(self,pid):
		lookup = cfg.PID[self.type()]
		# Need to check and make sure pid is valid for the lookup
		if not lookup is None: 
			try:
				lookup_url = cfg.API_URL + '/pods?where={"'+lookup+'":"' + pid + '"}'
				print 'Pod lookup url: ' + lookup_url
				# Returns a list of _items.
				p = requests.get(lookup_url) 
			except:
				raise InvalidMessage('Unable to contact the API [pods]',status_code=503,payload={'pid':pid}) 
		
			if not p.status_code == requests.codes.ok:
				raise InvalidMessage('API error', status_code=400,payload={'status_code':p.status_code})
		try:	
			self.pod = p.json()["_items"][0] # Take the first item in the list.
		except:
			raise InvalidMessage('pod not found',status_code=400,payload={'pid':pid})








