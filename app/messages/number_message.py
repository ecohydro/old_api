from app.messages import Message

class NumberMessage(Message): 

	def __init__(self,data=None,config=None,db=None):
		super(NumberMessage,self).__init__(data=data,config=config,db=db)
		self.type = 'number'

	def pod_serial_number_length(self):
		return 0

	def podId(self):
		if self.podIdvalue == None:
			podurl = self.config['API_URL'] + '/pods/?where={"' + 'number' + '":"' + self.number + '"}'
			self.podIdvalue = str(requests.get(podurl).json()['_items'][0]['podId'])
		return self.podIdvalue

	def post(self):
		if not self.status == 'invalid':
			self.post_data()

	def parse(self):
		self.parse_message(i=2)
