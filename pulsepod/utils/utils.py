# Lots of stuff to import. 
import struct
import json
import time
import datetime
import struct
from  pulsepod.utils import cfg
from flask import current_app as app
from flask import jsonify
import requests
import werkzeug.exceptions
from random import choice, randint
from names import firstnames, lastnames


# Definie a exception class to report errors (handy for debugging)
class InvalidMessage(Exception):
	"""Raised when pdu2json cannot properly format the PDU submitted
    :param pdu_exception: the original exception raised by pdu2json
	"""
	status_code = 400
	def __init__(self, error, status_code=None, payload=None):
		Exception.__init__(self) 
		self.error = error
		if status_code is not None:
			self.status_code = status_code
		self.payload = payload
	
	def to_dict(self):
		rv = dict(self.payload or ())
		rv['error'] = self.error
		return rv
	
def pod_name():
	return choice(firstnames) + '-' + choice(lastnames) + '-' + str(randint(1000,9999))

##############################################
# PARSING UTILITIES 						 #
##############################################

def get_sensor(sid):
	sensor = {}
	sensor_url = cfg.API_URL + '/sensors/' + str(sid)
	try:
		s = requests.get(sensor_url)
	except:
		raise InvalidMessage('Unable to contact the API [sensors]',status_code=503) 
	if not s.status_code == requests.codes.ok:
		raise InvalidMessage('API unable to determine sensor information',\
			 				status_code=400,payload={'status_code':r.status_code})
	
	# sensor data is packed as a dict, but through a couple of layers
	try:
		sensor = s.json()
	except:
		raise InvalidMessage('Error getting sensor json from API',status_code=400)
			
	try:
		sensor['value_length'] = sensor['nbytes']
		sensor['fmt'] = sensor['byteorder'] + sensor['fmt'] 
	except:
		raise InvalidMessage('Error creating sensor variables',status_code=400)

	return sensor

def get_time(content,i):
	#parse unixtime to long int, then convert to database time
	try:
		unixtime = struct.unpack('<L', content[i:i+8].decode('hex'))[0]
	except:
		raise InvalidMessage('Error decoding timestamp',status_code=400)
	t = time.gmtime(unixtime)
	#dbtime is (e.g.) "Tue, 17 Sep 2013 01:33:56 GMT"
	dbtime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", t)
	return dbtime

def get_value(content,i,sensor):
	# parse value based on format string
	try:
		value = struct.unpack(str(sensor['fmt']), content[i:i+(2*int(sensor['value_length']))].decode('hex'))[0]
	except:
		raise InvalidMessage('Error parsing format string',status_code=400)
				
	# Right here we would do some initial QA/QC based on whatever 
	# QA/QC limits we eventually add to the sensor specifications.
	return float(value)



