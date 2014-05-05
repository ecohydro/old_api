import requests
from app.messages import Message 
from app.messages.invalid_message import InvalidMessage
from app.messages.status_message import StatusMessage
from app.messages.podid_message import PodIdMessage
from app.messages.number_message import NumberMessage
from app.messages.deploy_message import DeployMessage

class MessageFactory(object):
	@staticmethod
	def create(data=None, url=None, config=None, db=None):
		if not config:
			assert 0, "Must provide app.config"
		if not db:
			assert 0, "Must provide PyMongo db object"

		if data == None and url == None:
			assert 0, "Must provide a url or message data"
		if not url == None:
			try:
				r = requests.get(str(url))
				if r.status_code == requests.codes.ok:
					data = r.json()
				else:
					assert 0, "Bad url (" + str(r.status_code) + "): " + str(url) 
			except Exception as e:
				e.args += ("Connection error",str(url))
				raise

		try: # Catch invalid messages
			frame_number = int(str(data['message'][0:2]),16)
		except ValueError:
			frame_number = 99
		try: # Catch undefined Frame IDs.
			type = config['FRAMES'][frame_number]
		except KeyError:
			type = config['FRAMES'][99]
		if type == "number": 	return NumberMessage(data,config,db)
		if type == "pod_id": 	return PodIdMessage(data,config,db)
		if type == "status": 	return StatusMessage(data,config,db)
		if type == "invalid":	return InvalidMessage(data,config,db)
		if type == "deploy":	return DeployMessage(data,config,db)
		assert 0, "Bad SMS creation: " + type
