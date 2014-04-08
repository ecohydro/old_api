import os

# Get all the gateway settings, so we don't need to pass
#  them around or hack updates
# NOTE: Use 'import cfg' in every file where these 
#		variables are needed (every file)
# NOTE: Use 'import cfg' AFTER 'from rq import Worker' in 
# 		any worker scripts. failure to do so will cause 
#		worker jobs to fail on first execution.

# RQ/Worker stuff:
# REDISTOGO_URL must be set by heroku config:set.
REDIS_URL = os.getenv('REDISTOGO_URL','redis://localhost:6379')

# URLs for production on Heroku or local:
API_URL = os.getenv('API_URL','http://0.0.0.0:5000') 

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# EVE API status ERR response (who knows if this will 
# ever change):
ERR='ERR'
STATUS='_status'
ISSUES='_issues'


# POD DATA FRAMES 
# Dict of possible message frame IDs and corresponding types
# Used by Message class to determine message subclass
# pod_number: Is a data message sent without any ID 
#			   info other than phone number
# pod_status: Is a message sent containing pod cell id
#			   and sensor information
# pod_imei: Is a data message that includes the pod IMEI
# Any other id will be assigned invalid

FRAMES={
	0:'number',
	1:'status',
	2:'imei',
	3:'deploy',
	99:'invalid',
}

# Content-type Headers:
FORM='application/x-www-form-urlencoded; charset=UTF-8'
JSON='application/json'
ETAG='etag' # Will change to _etag sometime soon.
CREATED=201 # Eve returns 200 when a POST is valid 

IMEI_LENGTH = 2

