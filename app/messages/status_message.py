from app.messages import Message

class StatusMessage(Message):

	def __init__(self,data=None,config=None,db=None):
		super(StatusMessage,self).__init__(data=data,config=config,db=db)
		self.type = 'status'
		self.frame = self.__class__.__name__

	def parse(self):
		json = []
		i=2+self.pod_serial_number_length 
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
			raise InvalidMessageException('Status message improperly formatted', status_code=400, payload=payload)

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
		self.patch_status() 	  # update the pod if number has changed

