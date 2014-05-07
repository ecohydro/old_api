from app.messages import Message

class InvalidMessage(Message):

	def __init__(self,data=None,config=None,db=None):
		super(InvalidMessage,self).__init__(data=data,config=config,db=db)
		self.status = 'invalid'
		self.type = 'invalid'
		self.frame = self.__class__.__name__

	def parse(self):
		pass

	def post(self):
		pass

	def patch(self):
		patched = {}
		self.patch_message(patched)
