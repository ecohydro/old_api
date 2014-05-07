from app.messages import Message

class NumberMessage(Message): 

	def __init__(self,data=None,config=None,db=None):
		super(NumberMessage,self).__init__(data=data,config=config,db=db)
		self.type = 'data'
		self.frame = self.__class__.__name__
		self.pod_serial_number_length = 0

	def pod_id(self):
		# USE PYMONGO HERE
		if self.pod_id_value == None:
			podurl = self.config['API_URL'] + '/pods/?where={"' + 'number' + '":"' + self.number + '"}'
			self.pod_id_value = str(requests.get(podurl).json()['_items'][0]['pod_id'])
		return self.pod_id_value

	def post(self):
		if not self.status == 'invalid':
			self.post_data()

		
