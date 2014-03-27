# SMS Frames. These are hand-crafted parsers based on the structure of pod SMS messages.
import requests
import json
import os


from pulsepod.SMS import SMS
from pulsepod.utils import cfg
from pulsepod.utils.utils import InvalidMessage
from pulsepod.utils.utils import update_voltage, get_sensor, get_time, get_value

def pod_number_post(message):
 	status = post_data(message)
 	return status

# 	dataurl = cfg.API_URL + '/data'
# 	headers = {'content-type':'application/json'}
# 	d = requests.post(url=dataurl, data=json.dumps(message.data), headers=headers) 
# 	return d.status_code # RQ REPORTING

def pod_imei_post(message):
 	status = post_data(message)
 	return status

# 	dataurl = cfg.API_URL + '/data'
# 	headers = {'content-type':'application/json'}
# 	d = requests.post(url=dataurl, data=json.dumps(message.data), headers=headers) 
# 	return d.status_code # RQ REPORTING

def pod_status_post(message):
	return 200

def invalid_post(message):
	return None

##############################################
# POSTING FUNCTIONS	    					 #
##############################################
def post_data(message):
	nposted = 0
	dataids = []
	dataurl = cfg.API_URL + '/data'
	headers = {'content-type':'application/json'}
	d = requests.post(url=dataurl, data=json.dumps(message.data), headers=headers)
	print d.status_code
	if d.status_code == cfg.CREATED:
		items = d.json()
		for item in items:
			print 'Item status: ' + item[cfg.STATUS]
			if not item[cfg.STATUS] == cfg.ERR:
				nposted = nposted + 1
				message.data_ids.append(item[u'_id'])
	message.nposted = nposted
	return message # RQ REPORTING

##############################################
# PARSING FUNCTIONS 						 #
##############################################
def invalid_parse(message):
	message.status = 'invalid'
	return message

def pod_number_parse(message):
	message.data = []
	i=2 # Start at position 2 in the frame, since FrameID is position 1. 
	total_obs=0 # Initialize observation counter
	"""
    go through the user data of the message
    | sid | nObs | unixtime1 | value1 | unixtime2 | value2 | ... | valueN |
    sid = 1byte
    nObs = 1byte
    unixtime = 4 bytes LITTLE ENDIAN
    value = look up length
    """
    # Assigns pod info to message.pod:
	message.get_pod(str(message.number))
	payload = {'_id':message._id,'type':message.type(),'content':message.content,'frame_id':message.frame_id()}
	while i <len(message.content):
		sensor={} # Reset sensor information
		try:
			sid = int(message.content[i:i+2], 16)
		except:
			raise InvalidMessage('Error reading sid',status_code=400)

		sensor = get_sensor(sid) # Retrieve sensor information from API
		i += 2
		nobs = int(message.content[i:i+2], 16) # Read nObs from message content
		i += 2
		total_obs = total_obs + nobs
		# add entry for each observation (nObs) by the same sensor
		while nobs > 0:
			try:
				entry = {'s': str(sensor['name']), 'p': str(message.number), 'sensor': str(sensor['_id']), 'pod':str(message.pod['_id'])}
			except:
				raise InvalidMessage('Error reading sensorname or address', status_code=400)
			
			entry['t'] = get_time(message.content,i) # Get the timestamp 
			i += 8

			entry['v'] = get_value(message.content,i,sensor) # Read the value			
			i += 2*sensor['value_length']
							
			# add to big ole json thing
			message.data.append(entry)
				
			nobs -= 1
	message.nobs = total_obs
	message.status = 'parsed'
	return message


def pod_imei_parse(message):
	message.data = []
	i=2 # Start at position 2 in the frame, since FrameID is position 1.
	total_obs=0 # Initialize observation counter
	# IMEI message
	#
	# Whatever we decide to do....
	imei_length = 2 # BEN EDIT TO CORRECT LENGTH
	message.imei = int(message.content[i:i+imei_length], 16) 
	i += imei_length			

	payload = {'_id':message._id,'type':message.type(),'content':message.content,'frame_id':message.frame_id()}
	while i <len(message.content):
		sensor={} # Reset sensor information
		try:
			sid = int(message.content[i:i+2], 16)
		except:
			raise InvalidMessage('Error reading sid',status_code=400,payload=payload)

		sensor = get_sensor(sid) # Retrieve sensor information from API
		i += 2
		nobs = int(message.content[i:i+2], 16) # Read nObs from message content
		i += 2
		total_obs = total_obs + nobs
		# add entry for each observation (nObs) by the same sensor
		while nobs > 0:
			try:
				entry = {'s': str(sensor.name), 'p': str(message.number), 'sensor': str(sensor._id), 'pod':str(message.pod['_id'])}
			except:
				raise InvalidMessage('Error reading sensorname or address', status_code=400,payload=payload)
			
			entry['t'] = get_time(message.content,i) # Get the timestamp 
			i += 8

			entry['v'] = get_value(message.content,i,sensor) # Read the value			
			i += 2*sensor.value_length
				
			entry['imei'] = message.imei # Add the IMEI for this entry			
			# add to big ole json thing
			message.data.append(entry)
				
			nobs -= 1

	# If successfully parsed, put message.status to 'parsed'  
 	message.status='parsed'
 	message.nobs = total_obs
	return message

def pod_status_parse(message):
	json = []
	i=2 # Start at position 2 in the frame, since FrameID is position 1. 
	# Deployment message
	##################################################################
	# |   LAC  |   CI   | nSensors |  sID1  |  sID1  | ... |  sIDn  |
	# | 2 byte | 2 byte |  1 byte  | 1 byte | 1 byte | ... | 1 byte |
	##################################################################
	# make sure message is long enough to read everything
	payload = {'_id':message._id,'type':message.type(),'content':message.content,'frame_id':message.frame_id()}
	if len(message.content) < 12:
		raise InvalidMessage('Status message too short', status_code=400, payload=payload)
	lac = int(message.content[i:i+4], 16)
	i += 4
	cell_id = int(message.content[i:i+4], 16)
	i += 4
	n_sensors = int(message.content[i:i+2], 16)
	i += 2
	# now make sure length is actually correct
	if len(message.content) != 12 + 2*n_sensors:
		raise InvalidMessage('Status message improperly formatted', status_code=400, payload=payload)

	# sIDs is list of integer sIDs
	sids = []

	for j in range(n_sensors):
		sids.append(int(message.content[i:i+2], 16))
		i += 2

	message.data = {'lac': lac, 'ci': cell_id, 'nSensors': n_sensors, 'sensorlist': sids}
	return message

