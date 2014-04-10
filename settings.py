
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
	'notebook':{
		'type':'objectid',
		'data_relation': {
			 'resource': 'notebooks',
			 'field': '_id',
			 'embeddable':True
		},
	},				   # nbkId
	'pod':{
		'type':'objectid',
		'data_relation': {
			 'resource': 'pods',
			 'field': '_id',
			 'embeddable':True
		},
	},
	'sensor':{
		'type':'objectid',
		'data_relation': {
			'resource': 'sensors',
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
	'nbkId' : {
		'type': 'string',
		'unqiue': True,
		'required': True,
		'maxlength': 10,
		'minlength': 10,
	},
	'name' : {
		'type': 'string',
		'maxlength':100,
		'required':True
	},
	'last': {
		'type':'datetime',
	},
	'owner': {
		'type':'string',
		'required': True,
	},
	'shared': {
		'type':'list',
		'schema': {
			'type':'string'
		},
		'required': True,
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
	},
	'favorite': {
		'type':'number',
		'required':False,
	},
	'status': {
		'type': 'string',
		'allowed': ['dead','deployed','provisioned','active','unknown'],
		'required':False,
		'default' : 'provisioned'
	},
	# Information about what sensors are included in this notebook:
	'sensors': {
		'type': 'list',
		'schema': {
			'type':'objectid', # is objectid for API embedded (remove sids from default projection)
			'data_relation': { 
				'resource':'sensors',
				'field': '_id',
				'embeddable': True
			},
		},
	},
	# sids facilitate lookups in meteor. May not need this. 
	# Depends on how the $in mongodb query behaves with objectids in meteor (likely badly)
	'sids': {	
		'type': 'list',
		'schema': {
			'type':'number'
		}
	},
	# Tags related to the location and user-supplied information about this notebook
	# (not yet implemented)
	'tags': {
		'type': 'list',
		'schema': {'type':'string'}
	},
	# Location information for this notebook
	'location': {
		'type':'dict',
		'schema': {
			'lat':{'type':'number','required':True},
			'lng':{'type':'number','required':True},
			'accuracy':{'type':'number','required':True}
		},
	},
	'elevation' : {
		'type':'dict',
		'schema': {
			'elevation':{'type':'number','required':True,'default':-9999},
			'resolution':{'type':'number','required':True,'default':-9999}
		}
	},
	# Notebook cellular information:
	'cellTowers':{ # Follows the Google Location API schema
		'type':'dict',
		'schema':{
			'cellId':{'type':'number','required':True,'default':39627456},
			'locationAreaCode':{'type':'number','required':True,'default':40495},
			'mobileCountryCode':{'type':'number','required':True,'default':310},
			'mobileNetworkCode':{'type':'number','required':True,'default':260},
			'age':{'type':'number','required':False}
		},
	},
	'address' : {
		'type':'dict',
		'schema':{
			'formatted_address':{'type':'string','required':False,'default':'unknown'},
			'street_address':{'type':'dict',
				'schema': {
					'short':{'type':'string','required':False,'default':'none'},
					'full':{'type':'string','required':False,'default':'none'},
				},
			},
			'route':{'type':'dict',
				'schema': {
					'short':{'type':'string','required':False,'default':'unknown'},
					'full':{'type':'string','required':False,'default':'unknown'},
				},
			},
			'country':{'type':'dict',
				'schema': {
					'short':{'type':'string','required':False,'default':'none'},
					'full':{'type':'string','required':False,'default':'none'},
				},
			},
			'administrative_area_level_1':{'type':'dict',
				'schema': {
					'short':{'type':'string','required':False,'default':'unknown'},
					'full':{'type':'string','required':False,'default':'unknown'},
				},
			},
			'administrative_area_level_2':{'type':'dict',
				'schema': {
					'short':{'type':'string','required':False,'default':'unknown'},
					'full':{'type':'string','required':False,'default':'unknown'},
				},
			},
			'administrative_area_level_3':{'type':'dict',
				'schema': {
					'short':{'type':'string','required':False,'default':'unknown'},
					'full':{'type':'string','required':False,'default':'unknown'},
				},
			},
			'locality':{'type':'dict',
				'schema': {
					'short':{'type':'string','required':False,'default':'unknown'},
					'full':{'type':'string','required':False,'default':'unknown'},
				},
			},
			'intersection':{'type':'string','required':False},
			'colloquial_area':{'type':'string','required':False},
			'sublocality':{'type':'string','required':False},
			'sublocality_level_1':{'type':'string','required':False},
			'sublocality_level_2':{'type':'string','required':False},
			'sublocality_level_3':{'type':'string','required':False},
			'sublocality_level_4':{'type':'string','required':False},
			'sublocality_level_5':{'type':'string','required':False},
			'neighborhood':{'type':'string','required':False},
			'premise':{'type':'string','required':False},
			'subpremise':{'type':'string','required':False},
			'postal_code':{'type':'string','required':False,'default':'unknown'},
			'natural_feature':{'type':'string','required':False},
			'airport':{'type':'string','required':False},
			'park':{'type':'string','required':False},
			'point_of_interest':{'type':'string','required':False},
			'floor':{'type':'string','required':False},
			'establishment':{'type':'string','required':False},
			'parking':{'type':'string','required':False},
			'post_box':{'type':'string','required':False},
			'postal_town':{'type':'string','required':False},
			'room':{'type':'string','required':False},
			'street_number':{'type':'string','required':False},
			'bus_station':{'type':'string','required':False},
			'train_station':{'type':'string','required':False},
			'transit_station':{'type':'string','required':False}
		}
	},
	# need to add geocoding information to the notebook...
	# need to add notes to notebook...
	# a users list would allow sharing of notebooks...
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
	'owner' : {
		'type':'string',
		'required':True,
		'maxlength':25,
		'minlength':15,
	},
	'podId' : { # Pod ID for use in SMS
		'type':'string',
		'minlength':10,
		'maxlength':10,
		'required':True,
		'unique': True,
	},
	'notebook' : { # Pod ID (usually phone number)
		'type':'objectid',
		'data_relation': {
			 'resource': 'notebooks',
			 'field': '_id',
			 'embeddable':True
		},
	},
	'number' : {  # Pod number (E.164 format)
		'type':'string',
		'minlength':10,
		'maxlength':15,
		'required':True,
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
		'default':0,
		'required':False
	},
	'mode': {
		'type': 'string',
		'allowed': ['teen','asleep','normal'],
		'default' : 'normal'
	},
	'radioType':{
		'type': 'string',
		'allowed': ['gsm','cdma','wcdma'],
		'required':True,
		'defaul':'gsm',
	},
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
	'context': {
		'type': 'string',
		'required': True,
		'default': ''
	},
	'variable': {
		'type': 'string',
		'required': True,
		'default': ''
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
	
	# Units: A text string that identifies the units for sensor values
	'units' : {
		'type':'string',
		'required':False,
		'maxlength':100,
	},	
	'm' : {
		'type':'number',
		'required':False,
		'default':1
	},
	'b' : { 
		'type':'number',
		'required':False,
		'default':0
	}
}

messages_schema = {
	# Schema definition, based on Cerberus grammar. Check the Cerberus project
	# (https://github.com/nicolaiarocci/cerberus) for details.
	# Note: using short variable names to save space in MongoDB.
	'message':{
		'type':'string',
		'required':True,
		'maxlength':170,
		'unique':False,
		},
	'status':{
		'type':'string',
		'required':True,
		'allowed':['queued','parsed','posted','unknown','invalid'],
		'default':'queued',
	},
	'id':{
		'type':'string',
		'required':True,
		'maxlength':20,
	},
	'number':{
		'type':'string',
		'required':True,
		'maxlength':20,
	},
	't':{
		'type':'datetime',
		'required':False,
	},
	'source':{
		'type':'string',
		'required':True,
		'allowed':['smssync','twilio','nexmo'],
	}, 
	'type':{
		'type':'string',
		'required':False,
		'allowed':['unknown','status','deploy','invalid','number','imei'],
		'default':'unknown'
	},
	'data':{
		'type':'list',
		'schema':{
			'type':'objectid', # becomes objectid when gateway and evepod are consolidated
			'data_relation': { 
				'resource':'data',
				'field': '_id',
				'embeddable': True
			},
		}
	},
	'nobs':{
		'type':'number',
		'required':False,
		'default':0
	},
	'nposted':{
		'type':'number',
		'required':'False',
		'default':0
	},
	'notebook':{
		'type':'objectid',
		'data_relation': {
			 'resource': 'notebooks',
			 'field': '_id',
			 'embeddable':True
		},
	},				   # nbkId
	'pod':{
		'type':'objectid',
		'data_relation': {
			 'resource': 'pods',
			 'field': '_id',
			 'embeddable':True
		},
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
		'field': 'podId'
	},

	# We choose to override global cache-control directives for this resource.
	'cache_control': 'max-age=10,must-revalidate',
	'cache_expires': 10,

	# most global settings can be overridden at resource level
	'resource_methods': ['GET','POST'],
	'item_methods': ['GET','PATCH'],

	# Public read-only access:
#	'public_methods': ['GET'],
#    'public_item_methods': ['GET'],

	'schema': pod_schema,
	'datasource':{
		'default_sort':[('_created',-1)],
	},
	'versioning':True
}

data = {
	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST'],
	'schema': data_schema,
	'datasource':{
		'default_sort':[('_created',-1)],
	}
}


notebooks = {
	'additional_lookup': {
		'url' : 'regex("[\w]+")',
		'field': 'nbkId'
	},
	# most global settings can be overridden at resource level
	'resource_methods': ['GET', 'POST'],
	'schema': notebook_schema,
	'datasource':{
		'default_sort':[('_created',-1)],
	}
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
		'field': 'sid'
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

# MESSAGES RESOURCE DOMAINS:
smssync = {
	# most global settings can be overridden at resource level
	'url':'messages/smssync',
	'resource_methods': ['GET', 'POST'],
	'schema': messages_schema,
	'allow_unknown':True,
	'datasource':{
		'default_sort':[('_created',-1)]
	},
}
twilio = {
	# most global settings can be overridden at resource level
	'url':'messages/twilio',
	'resource_methods': ['GET', 'POST'],
	'schema': messages_schema,
	'allow_unknown':True,
	'additional_lookup': {
		'url' : 'regex("[\w]+")',
		'field': 'id'
	},
	'datasource':{
		'default_sort':[('_created',-1)]
	},
}
nexmo = {
	# most global settings can be overridden at resource level
	'url':'messages/nexmo',
	'resource_methods': ['GET', 'POST'],
	'schema': messages_schema,
	'allow_unknown':True,
	'additional_lookup': {
		'url' : 'regex("[\w]+")',
		'field': 'id'
	},
	'datasource':{
		'default_sort':[('_created',-1)]
	},
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
		'smssync':smssync,
		'twilio':twilio,
		'nexmo':nexmo,
}

