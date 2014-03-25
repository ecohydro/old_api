
#------------------------------------------------------------------------------
#
# GLOBAL SETTINGS
#
# Defines: gateway_schema, dataset_schema, pod_schema, user_schema,
#
#------------------------------------------------------------------------------
import os

# FIGURE OUT WHERE WE ARE RUNNING... ON HEROKU, OR LOCALLY?
MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_PORT = os.getenv('MONGO_PORT')
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_DBNAME = os.getenv('MONGO_DBNAME')

SERVER_NAME = os.getenv('SERVER_NAME')

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST']

# Enable reads (GET), edits (PATCH) and deletes of individual items
# (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH']

# Set the public methods for the read-only API. 
# Only authorized users can write, edit and delete
# PUBLIC_METHODS = ['GET'] 
# PUBLIC_ITEM_METHODS = ['GET']

#------------------------------------------------------------------------------
#
# RESOURCE SCHEMAS
#
# Defines: 	gateway_schema, dataset_schema, pod_schema, user_schema,
#			allsensorinfo, allpoddata, allfarmerdata, farmers 
#
#------------------------------------------------------------------------------

data_schema = {
	# Schema definition, based on Cerberus grammar. Check the Cerberus project
	# (https://github.com/nicolaiarocci/cerberus) for details.
	# Note: using short variable names to save space in MongoDB.
	't':{'type':'datetime','required':True},   # datetime 
	'v':{'type':'float','required':True},      # value
	'p':{'type':'string','required':True},     # pod
	's':{'type':'string','required':True},     # sensor name
	'nbkId':{'type':'string'},				   # nbkId

	'sensor':{
		'type':'objectid',
		'data_relation': {
			'resource': 'sensors',
			'field': '_id',
			'embeddable': True
		},
	},

	'pod':{
		'type':'objectid',
		'data_relation': {
			'resource': 'pods',
			'field': '_id',
			'embeddable': True
		},
	},
	
	'notebook':{
		'type':'objectid',
		'data_relation': {
			'resource': 'notebooks',
			'field': '_id',
			'embeddable': True
		},
	},
}

user_schema = {
	# Schema definition, based on Cerberus grammar. Check the Cerberus project
	# (https://github.com/nicolaiarocci/cerberus) for detailsself.
	# Only keys are stored on evepod. All user information is stored on stormpath
	'keys': {'type': 'list','items':[{'type':'string'}]},
}

notebook_schema = {
	# Schema definition, based on Cerberus grammar. Check the Cerberus project
	# (https://github.com/nicolaiarocci/cerberus) for details.
	# Sensor text ID for use in URLs and in API data queries/submissions
	'name' : {
		'type': 'string',
		'maxlength':60,
		'required':True
	},
	'pod_list' : {
		'type':'list','items':[{
			'type':'objectid'
		}],
		'required': False,
	},
	'owner' :  {
		'type' : 'string', # will be objectid eventually
		'maxlength' : 30,  # will be objectid limit eventually
		'required' : False,
	},
	'public': {
		'type':'boolean',
		'required': False,
		'default': True
	},
	'pod' : {
		'type':'objectid',
		'data_relation': {
			'resource': 'pods',
			'field': '_id',
			'embeddable': True
		}
	},
	# need to add spatial information to notebook.
	# need to add notes to notebook.
	# A users list will allow sharing of notebooks.
}

pod_schema = { 
	# Schema definition, based on Cerberus grammar. Check the Cerberus project
	# (https://github.com/nicolaiarocci/cerberus) for details.
	# Sensor text ID for use in URLs and in API data queries/submissions
	'name' : { # Pod URL name (use the pod name generator)
		'type': 'string',
		'minlength': 10,
		'maxlength': 40,
		'required': True,
		'unique': True,
	},
	'pid' : { # Pod ID (usually phone number)
		'type':'string',
		'minlength':10,
		'maxlength':15,
		'required':False,
		'unique': False,
	},
	'number' : {  # Pod number (E.164 format)
		'type':'string',
		'minlength':10,
		'maxlength':15,
		'required':False,
		'unique':False,
	},
	'imei':{ # IMEI address of cellular radio, acts as Serial Number for the Pod
		'type':'string', # Need to define an IMEI address type
		'unique':True,
		'required':True,
		'minlength':15,
		'maxlength':20,
	},
	'firmware':{
		'type':'integer',
		'minlength':1,
		'maxlength':2,
		'default':0
	},
	'status': {
		'type': 'string',
		'allowed': ['dead','deployed','provisioned','active','unknown'],
		'required':False,
		'default' : 'provisioned'
	},
	'mode': {
		'type': 'string',
		'allowed': ['teen','asleep','normal'],
		'default' : 'normal'
	},
	'last': {
		'type':'datetime',
	},
	'owner': {
		'type':'string',
		'required': False,
		'default': 'qcjPMcLwR3xWAHFrm'
	},
	'public': {
		'type':'boolean',
		'required': False,
		'default': True
	},
	'voltage':{
		'type':'number',
		'required':False,
		'default':0
	}
	
}

sensor_schema = { 
	# Schema definition, based on Cerberus grammar. Check the Cerberus project
	# (https://github.com/nicolaiarocci/cerberus) for details.
	# Sensor text ID for use in URLs and in API data queries/submissions
	'name' : {
		'type': 'string',
		'minlength': 1,
		'maxlength': 16,
		'required': True,
	},
	# Unique sensor ID. SID will be referenced in the PUD but should NOT be used elsewhere
	'sid' : {
		'type': 'integer',
		'minlength': 1,
		'maxlength': 3,
		'required': True,
		'unique': True,
	},
	# Number of bytes required for each piece of sensor data
	'nbytes' : {
		'type':'integer',
		'required':True,
	},
	# Format of data values, based on structs library http://docs.python.org/2/library/struct.html
	'fmt' : {
		'type':'string',
		'required':True,
		'minlength':1,
		'maxlength':1,
		'allowed': ['x','c','b','B','?','h','H','i','I','l','L','q','Q','f','d','s','p','P'],
	},
	
	
	# Byte order of data values, based on structs library http://docs.python.org/2/library/struct.html
	'byteorder' : {
		'type':'string',
		'required':False,
		'minlength':1,
		'maxlength':1,
		'allowed': ['@','=','<','>','!'],
		'default':'<',
	},
	
	# Sensor info: A text string that provides summary info for each sensor
	'info' : {
		'type':'string',
		'required':False,
		'minlength':1,
		'maxlength':256,
		'default':'no additional information is available for this sensor',
	},

	# Magnitude: A multiplier for sensor values
	'magnitude' : {
		'type':'float',
		'required':False,
		'maxlength':100,
		'default':1.0,
	},
	
	# Units: A text string that identifies the units for sensor values
	'units' : {
		'type':'string',
		'required':False,
		'maxlength':100,
	},	
	
}

#------------------------------------------------------------------------------
#
# RESOURCE DEFINITIONS
#
# Defines: pods,
#
#------------------------------------------------------------------------------
pods = {
	# 'title' tag used in item links. Defaults to the resource title minus
	# the final, plural 's' (works fine in most cases but not for 'people')
	# 'item_title': 'p',
	# by default the standard item entry point is defined as
	# '/<item_title>/<ObjectId>/'. We leave it untouched, and we also enable an
	# additional read-only entry point. This way consumers can also perform
	# GET requests at '/<item_title>/<urlname>/'.
	'additional_lookup': {
		'url' : 'regex("[\w]+")',
		'field': 'name'
	},

#	'datasource': {
#        'projection': {	'owner': 0,
#        				'firmware': 0,
#        			},
#     },

	# We choose to override global cache-control directives for this resource.
	'cache_control': 'max-age=10,must-revalidate',
	'cache_expires': 10,

	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST'],
	'item_methods': ['GET','PATCH'],

	# Public read-only access:
#	'public_methods': ['GET'],
#    'public_item_methods': ['GET'],

	'schema': pod_schema
}

data = {
	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST'],
	'schema': data_schema	
}


notebooks = {
	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST'],
	'schema': notebook_schema
}

users = {
	# 'title' tag used in item links. Defaults to the resource title minus
	# the final, plural 's' (works fine in most cases but not for 'people')
	# 'item_title': 'f',
	# by default the standard item entry point is defined as
	# '/<item_title>/<ObjectId>/'. We leave it untouched, and we also enable an
	# additional read-only entry point. This way consumers can also perform
	# GET requests at '/<item_title>/<username>/'.

	# We choose to override global cache-control directives for this resource.
	'cache_control': '',
	'cache_expires': 0,
		
	# Resource security:
	# No public methods on users
#	 #'public_methods': [],
#    'public_item_methods': [],

	# Only allow superusers and admin
	# 'allowed_roles': ['superuser', 'admin'],

	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST', 'DELETE'],	
	'schema': user_schema
}

sensors = {
	# 'title' tag used in item links. Defaults to the resource title minus
	# the final, plural 's' (works fine in most cases but not for 'people')
	# 'item_title': 'f',
	# by default the standard item entry point is defined as
	# '/<item_title>/<ObjectId>/'. We leave it untouched, and we also enable an
	# additional read-only entry point. This way consumers can also perform
	# GET requests at '/<item_title>/<lastname>/'.
	'additional_lookup': {
		'url' : 'regex("[\w]+")',
		'field': 'name'
	},
	# We choose to override global cache-control directives for this resource.
	'cache_control': 'max-age=10,must-revalidate',
	'cache_expires': 10,
	
	# Public read-only access:
#	'public_methods': ['GET'],
#    'public_item_methods': ['GET'],

	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST'],
	'schema': sensor_schema
}
#------------------------------------------------------------------------------
#
# DOMAINS
#
# Uses: pods, users, farmers, gateways, sensors, datasets
#
#------------------------------------------------------------------------------

DOMAIN = {
    	'pods': pods,
		'users':users,
		'sensors':sensors,
		'data':data,
		'notebooks':notebooks,
}

