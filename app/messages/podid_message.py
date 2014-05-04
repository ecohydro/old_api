from app.messages import Message

class PodIdMessage(Message):

	def __init__(self,data=None,config=None,db=None):
		super(PodIdMessage,self).__init__(data=data,config=config,db=db)
		self.type = 'pod_id'
	
	def post(self):
		if not self.status == 'invalid':
			self.post_data()

	def parse(self):
		self.parse_message(i=2+self.pod_serial_number_length())
	