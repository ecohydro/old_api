# # -----------------------------------------------------------------------------
# #
# # RESOURCE SCHEMAS
# #
# # Defines:     gateway_schema, dataset_schema, pod_schema, user_schema,
# #            allsensorinfo, allpoddata, allfarmerdata, farmers
# #
# # -----------------------------------------------------------------------------

# data_schema = {
#     # Schema definition, based on Cerberus grammar. Check the Cerberus project
#     # (https://github.com/nicolaiarocci/cerberus) for details.
#     # Note: using short variable names to save space in MongoDB.
#     't': {'type': 'datetime', 'required': True},                # datetime
#     'v': {'type': 'float', 'required': False, 'default': '1'},  # value
#     'p': {'type': 'string', 'required': True},      # pod
#     'n': {'type': 'string', 'required': True},      # notebook
#     's': {'type': 'string', 'required': True},      # sensor name
#     'loc': {
#         'type': 'dict',
#         'schema': {
#             'type': {'type': 'string', 'default': 'Point'},
#             'coordinates': {
#                 'type': 'list',
#                 'items': [
#                     {
#                         'type': 'number',
#                         'default': 0
#                     },
#                     {
#                         'type': 'number',
#                         'default': 0
#                     }
#                 ]
#             }
#         },
#         'required': True
#     },
#     # 'pod': {
#     #     'type': 'dict',
#     #     'schema': {
#     #         '_id': {'type': 'objectid'},
#     #         '_notebook': {'type': 'integer'}
#     #     },
#     #     'data_relation': {
#     #         'resource': 'pods',
#     #         'field': '_id',
#     #         'embeddable': True,
#     #         'version': True
#     #     },
#     # },
#     'pod': {
#         'type': 'objectid',
#         'data_relation': {
#             'resource': 'pods',
#             'field': '_id',
#             'embeddable': True
#         },
#     },
#     'notebook': {
#         'type': 'objectid',
#         'data_relation': {
#             'resource': 'notebooks',
#             'field': '_id',
#             'embeddable': True
#         },
#     },
#     'sensor': {
#         'type': 'objectid',
#         'data_relation': {
#             'resource': 'sensors',
#             'field': '_id',
#             'embeddable': True
#         },
#     },
# }

# user_schema = {
#     # Schema definition, based on Cerberus grammar. Check the Cerberus project
#     # (https://github.com/nicolaiarocci/cerberus) for detailsself.
#     'keys': {'type': 'list', 'items': [{'type': 'string'}]},
# }

# pod_schema = {
#     # Non-versioned pod data:
#     # Non-versioned pod data should be consistent for any notebook.
#     # These are fixed attributes of the pod itself, or dynamic attributes
#     # that do not need to be associated with notebooks.
#     # Original Pod schema:
#     # Sensor text ID for use in URLs and in API data queries/submissions
#     # Provisioning Properties (MUST BE SENT WITH POST):
#     # THESE SHOULD BE IN PODS:
#     'name': {  # Pod URL name (use the pod name generator)
#         'type': 'string',
#         'minlength': 10,
#         'maxlength': 60,
#         'required': True,
#         'unique': True,
#         'versioned': False,
#     },
#     'owner': {
#         'type': 'string',
#         'required': True,
#         'maxlength': 25,
#         'minlength': 4,
#         'versioned': False,
#     },
#     'pod_id': {  # Pod ID for use in SMS messages.
#         'type': 'integer',
#         'max': 65535,
#         'min': 0,
#         'required': True,
#         'unique': True,
#         'versioned': False,
#         'default': 0
#     },
#     'qr': {
#         'type': 'string',
#         'required': False,
#         'unique': True,
#         'versioned': False,
#         'default': 'https://s3.amazonaws.com/pulsepodqrsvgs/default.svg',
#     },
#     'imei': {  # IMEI address of cellular radio,
#         'type': 'string',  # Need to define an IMEI address type
#         'unique': False,
#         'required': False,
#         'minlength': 14,
#         'maxlength': 16,
#         'versioned': False,
#         'default': '000000000000000'
#     },
#     # Non-provisioning fields:
#     # Let's just assume this is always GSM for now.
#     'radio': {
#         'type': 'string',
#         'allowed': ['gsm', 'cdma', 'wcdma', 'wifi', 'irridium'],
#         'required': False,
#         'default': 'gsm',
#         'versioned': False,
#     },
#     # Status Properties (returned via status resource calls)
#     'last': {    # Most recent reporting date
#         'type': 'datetime',
#         'versioned': False
#     },
#     'voltage': {
#         'type': 'number',
#         'required': False,
#         'default': 0,
#         'versioned': False
#     },
#     'mode': {
#         'type': 'string',
#         'allowed': ['inactive', 'teenager', 'asleep', 'normal'],
#         'default': 'inactive',
#         'versioned': False
#     },
#     'number': {  # Pod number (E.164 format)
#         'type': 'string',
#         'minlength': 10,
#         'maxlength': 15,
#         'required': False,
#         'versioned': False,
#         'default': '18005551212'
#     },
#     # THESE SHOULD BE IN PODS_NOTEBOOKS ('Versioned': True):
#     # Deployment specific data (versioned)
#     # Schema definition, based on Cerberus grammar. Check the Cerberus project
#     # (https://github.com/nicolaiarocci/cerberus) for details.
#     'nbk_name': {
#         'type': 'string',
#         'maxlength': 100,
#         'required': False,
#         'versioned': True,
#         'default': 'Default Notebook'
#     },
#     'nbk_id': {
#         'type': 'string',
#         'required': False,
#         'versioned': True,
#         'unique': True
#     },
#     # Information about what sensors are included in this notebook:
#     'sensors': {
#         'type': 'list',
#         'schema': {
#             'type': 'objectid',  # is objectid for API embedded
#             'data_relation': {
#                 'resource': 'sensors',
#                 'field': '_id',
#                 'embeddable': True
#             },
#         },
#         'versioned': True,
#     },
#     # sids facilitate lookups in meteor. May not need this.
#     # Depends on how the $in mongodb query behaves with objectids in meteor
#     'sids': {
#         'type': 'list',
#         'schema': {
#             'type': 'number'
#         },
#         'versioned': True,
#     },
#     # Location information for this notebook
#     'location': {
#         'type': 'dict',
#         'schema': {
#             'lat': {'type': 'number', 'required': False, 'default': 0},
#             'lng': {'type': 'number', 'required': False, 'default': 0},
#             'accuracy': {'type': 'number', 'required': False, 'default': 100},
#         },
#         'versioned': True,
#     },
#     'elevation': {
#         'type': 'dict',
#         'schema': {
#             'elevation': {'type': 'number', 'required': False, 'default': 0},
#             'resolution': {'type': 'number', 'required': False, 'default': 1}
#         },
#         'versioned': True
#     },
#     # Notebook cellular information:
#     'cellTowers': {  # Follows the Google Location API schema
#         'type': 'dict',
#         'schema': {
#             'cellId': {
#                 'type': 'number',
#                 'required': False,
#                 'default': 39627456
#             },
#             'locationAreaCode': {
#                 'type': 'number',
#                 'required': False,
#                 'default': 40495
#             },
#             'mobileCountryCode': {
#                 'type': 'number',
#                 'required': False,
#                 'default': 310
#             },
#             'mobileNetworkCode': {
#                 'type': 'number',
#                 'required': False,
#                 'default': 260
#             },
#             'age': {'type': 'number', 'required': False}
#         },
#         'versioned': True,
#     },
#     'address': {
#         'type': 'dict',
#         'schema': {
#             'formatted_address': {
#                 'type': 'string',
#                 'required': False,
#                 'default': 'unknown'
#             },
#             'street_address': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'none'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'none'},
#                 },
#             },
#             'route': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                 },
#             },
#             'country': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'none'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'none'},
#                 },
#             },
#             'administrative_area_level_1': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                 },
#             },
#             'administrative_area_level_2': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                 },
#             },
#             'administrative_area_level_3': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                 },
#             },
#             'locality': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                 },
#             },
#             'intersection': {'type': 'string', 'required': False},
#             'colloquial_area': {'type': 'string', 'required': False},
#             'sublocality': {'type': 'string', 'required': False},
#             'sublocality_level_1': {'type': 'string', 'required': False},
#             'sublocality_level_2': {'type': 'string', 'required': False},
#             'sublocality_level_3': {'type': 'string', 'required': False},
#             'sublocality_level_4': {'type': 'string', 'required': False},
#             'sublocality_level_5': {'type': 'string', 'required': False},
#             'neighborhood': {'type': 'string', 'required': False},
#             'premise': {'type': 'string', 'required': False},
#             'subpremise': {'type': 'string', 'required': False},
#             'postal_code': {
#                 'type': 'string',
#                 'required': False,
#                 'default': 'unknown'},
#             'natural_feature': {'type': 'string', 'required': False},
#             'airport': {'type': 'string', 'required': False},
#             'park': {'type': 'string', 'required': False},
#             'point_of_interest': {'type': 'string', 'required': False},
#             'floor': {'type': 'string', 'required': False},
#             'establishment': {'type': 'string', 'required': False},
#             'parking': {'type': 'string', 'required': False},
#             'post_box': {'type': 'string', 'required': False},
#             'postal_town': {'type': 'string', 'required': False},
#             'room': {'type': 'string', 'required': False},
#             'street_number': {'type': 'string', 'required': False},
#             'bus_station': {'type': 'string', 'required': False},
#             'train_station': {'type': 'string', 'required': False},
#             'transit_station': {'type': 'string', 'required': False}
#         },
#         'versioned': True,
#     },
#     # Tags for location and user-supplied information about this notebook
#     # (not yet implemented) [NOT SURE TAGS SHOULD BE IN API SCHEMA?]
#     'tags': {
#         'type': 'list',
#         'schema': {'type': 'string'},
#         'versioned': True,
#         'required': False,
#     }
# }

# notebook_schema = {
#     # THESE SHOULD BE NOTEBOOKS
#     # Deployment specific data
#     # Schema definition, based on Cerberus grammar. Check the Cerberus project
#     # (https://github.com/nicolaiarocci/cerberus) for details.
#     'nbk_id': {
#         'type': 'string',
#         'required': False,
#         'unique': True
#     },
#     'name': {
#         'type': 'string',
#         'maxlength': 100,
#         'required': False,
#         'default': 'Default Notebook'
#     },
#     # Information about what sensors are included in this notebook:
#     'sensors': {
#         'type': 'list',
#         'schema': {
#             'type': 'objectid',  # is objectid for API embedded
#             'data_relation': {
#                 'resource': 'sensors',
#                 'field': '_id',
#                 'embeddable': True
#             },
#         },
#     },
#     # sids facilitate lookups in meteor. May not need this.
#     # Depends on how the $in mongodb query behaves with objectids in meteor
#     'sids': {
#         'type': 'list',
#         'schema': {
#             'type': 'number'
#         },
#     },
#     # Location information for this notebook
#     'location': {
#         'type': 'dict',
#         'schema': {
#             'lat': {'type': 'number', 'required': False, 'default': 0},
#             'lng': {'type': 'number', 'required': False, 'default': 0},
#             'accuracy': {'type': 'number', 'required': False, 'default': 100},
#         },
#     },
#     'elevation': {
#         'type': 'dict',
#         'schema': {
#             'elevation': {'type': 'number', 'required': False, 'default': 0},
#             'resolution': {'type': 'number', 'required': False, 'default': 1}
#         },
#     },
#     # Notebook cellular information:
#     'cellTowers': {  # Follows the Google Location API schema
#         'type': 'dict',
#         'schema': {
#             'cellId': {
#                 'type': 'number',
#                 'required': False,
#                 'default': 39627456
#             },
#             'locationAreaCode': {
#                 'type': 'number',
#                 'required': False,
#                 'default': 40495
#             },
#             'mobileCountryCode': {
#                 'type': 'number',
#                 'required': False,
#                 'default': 310
#             },
#             'mobileNetworkCode': {
#                 'type': 'number',
#                 'required': False,
#                 'default': 260
#             },
#             'age': {'type': 'number', 'required': False}
#         },
#     },
#     'address': {
#         'type': 'dict',
#         'schema': {
#             'formatted_address': {
#                 'type': 'string',
#                 'required': False,
#                 'default': 'unknown'
#             },
#             'street_address': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'none'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'none'},
#                 },
#             },
#             'route': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                 },
#             },
#             'country': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'none'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'none'},
#                 },
#             },
#             'administrative_area_level_1': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                 },
#             },
#             'administrative_area_level_2': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                 },
#             },
#             'administrative_area_level_3': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                 },
#             },
#             'locality': {
#                 'type': 'dict',
#                 'schema': {
#                     'short': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                     'full': {
#                         'type': 'string',
#                         'required': False,
#                         'default': 'unknown'},
#                 },
#             },
#             'intersection': {'type': 'string', 'required': False},
#             'colloquial_area': {'type': 'string', 'required': False},
#             'sublocality': {'type': 'string', 'required': False},
#             'sublocality_level_1': {'type': 'string', 'required': False},
#             'sublocality_level_2': {'type': 'string', 'required': False},
#             'sublocality_level_3': {'type': 'string', 'required': False},
#             'sublocality_level_4': {'type': 'string', 'required': False},
#             'sublocality_level_5': {'type': 'string', 'required': False},
#             'neighborhood': {'type': 'string', 'required': False},
#             'premise': {'type': 'string', 'required': False},
#             'subpremise': {'type': 'string', 'required': False},
#             'postal_code': {
#                 'type': 'string',
#                 'required': False,
#                 'default': 'unknown'},
#             'natural_feature': {'type': 'string', 'required': False},
#             'airport': {'type': 'string', 'required': False},
#             'park': {'type': 'string', 'required': False},
#             'point_of_interest': {'type': 'string', 'required': False},
#             'floor': {'type': 'string', 'required': False},
#             'establishment': {'type': 'string', 'required': False},
#             'parking': {'type': 'string', 'required': False},
#             'post_box': {'type': 'string', 'required': False},
#             'postal_town': {'type': 'string', 'required': False},
#             'room': {'type': 'string', 'required': False},
#             'street_number': {'type': 'string', 'required': False},
#             'bus_station': {'type': 'string', 'required': False},
#             'train_station': {'type': 'string', 'required': False},
#             'transit_station': {'type': 'string', 'required': False}
#         },
#     },
#     # Tags for location and user-supplied information about this notebook
#     # (not yet implemented) [NOT SURE TAGS SHOULD BE IN API SCHEMA?]
# }

# status_schema = {
#     # Status Properties (returned via status resource calls)
#     'last': {    # Most recent reporting date
#         'type': 'datetime',
#     },
#     'voltage': {
#         'type': 'number',
#         'required': False,
#         'default': 0,
#     },
#     'mode': {
#         'type': 'string',
#         'allowed': ['teen', 'asleep', 'normal'],
#         'default': 'normal',
#     },
#     'number': {  # Pod number (E.164 format)
#         'type': 'string',
#         'minlength': 10,
#         'maxlength': 15,
#     },
#     'nbk_id': {
#         'type': 'string'
#     },
# }

# sensor_schema = {
#     # Schema definition, based on Cerberus grammar. Check the Cerberus project
#     # (https://github.com/nicolaiarocci/cerberus) for details.
#     # Sensor text ID for use in URLs and in API data queries/submissions
#     'name': {
#         'type': 'string',
#         'minlength': 1,
#         'maxlength': 16,
#         'required': True,
#     },
#     # Unique sensor ID.
#     'sid': {
#         'type': 'integer',
#         'minlength': 1,
#         'maxlength': 3,
#         'required': True,
#         'unique': True,
#     },
#     'context': {
#         'type': 'string',
#         'required': True,
#         'default': ''
#     },
#     'variable': {
#         'type': 'string',
#         'required': True,
#         'default': ''
#     },
#     # Number of bytes required for each piece of sensor data
#     'nbytes': {
#         'type': 'integer',
#         'required': True,
#     },
#     # Format of data values, based on structs library
#     'fmt': {
#         'type': 'string',
#         'required': True,
#         'minlength': 1,
#         'maxlength': 1,
#         'allowed': ['x', 'c', 'b', 'B', '?', 'h', 'H',
#                     'i', 'I', 'l', 'L', 'q', 'Q', 'f', 'd', 's', 'p', 'P'],
#     },

#     # Byte order of data values, based on structs library
#     'byteorder': {
#         'type': 'string',
#         'required': False,
#         'minlength': 1,
#         'maxlength': 1,
#         'allowed': ['@', '=', '<', '>', '!'],
#         'default': '<',
#     },

#     # Sensor info: A text string that provides summary info for each sensor
#     'info': {
#         'type': 'string',
#         'required': False,
#         'minlength': 1,
#         'maxlength': 256,
#         'default': 'no additional information is available for this sensor',
#     },

#     # Units: A text string that identifies the units for sensor values
#     'units': {
#         'type': 'string',
#         'required': False,
#         'maxlength': 100,
#     },
#     'm': {
#         'type': 'number',
#         'required': False,
#         'default': 1
#     },
#     'b': {
#         'type': 'number',
#         'required': False,
#         'default': 0
#     }
# }

# messages_schema = {
#     # Schema definition, based on Cerberus grammar. Check the Cerberus project
#     # (https://github.com/nicolaiarocci/cerberus) for details.
#     # Note: using short variable names to save space in MongoDB.
#     'message': {
#         'type': 'string',
#         'required': True,
#         'maxlength': 170,
#         'unique': False,
#         },
#     'status': {
#         'type': 'string',
#         'required': True,
#         'allowed': ['queued', 'parsed', 'posted', 'unknown', 'invalid'],
#         'default': 'queued',
#     },
#     'id': {
#         'type': 'string',
#         'required': True,
#         'maxlength': 40,
#     },
#     'number': {
#         'type': 'string',
#         'required': True,
#         'maxlength': 20,
#     },
#     't': {
#         'type': 'datetime',
#         'required': False,
#     },
#     'source': {
#         'type': 'string',
#         'required': True,
#         'allowed': ['smssync', 'twilio', 'nexmo'],
#     },
#     'type': {
#         'type': 'string',
#         'required': False,
#         'allowed': ['unknown', 'status', 'deploy',
#                     'invalid', 'data'],
#         'default': 'unknown'
#     },
#     'nobs': {
#         'type': 'number',
#         'required': False,
#         'default': 0
#     },
#     'nposted': {
#         'type': 'number',
#         'required': 'False',
#         'default': 0
#     },
# }


# # -----------------------------------------------------------------------------
# #
# # RESOURCE DEFINITIONS
# #
# # Defines: pods,
# #
# # -----------------------------------------------------------------------------
# pods = {
#     # 'title' tag used in item links. Defaults to the resource title minus
#     # the final, plural 's' (works fine in most cases but not for 'people')
#     # 'item_title': 'p',
#     # by default the standard item entry point is defined as
#     # '/<item_title>/<ObjectId>/'. We leave it untouched, and we also enable an
#     # additional read-only entry point. This way consumers can also perform
#     # GET requests at '/<item_title>/<urlname>/'.
#     'additional_lookup': {
#         'field': 'pod_id'
#     },

#     # We choose to override global cache-control directives for this resource.
#     'cache_control': 'max-age=10,must-revalidate',
#     'cache_expires': 10,

#     # most global settings can be overridden at resource level
#     'resource_methods': ['GET', 'POST'],
#     'item_methods': ['GET', 'PUT', 'PATCH', 'DELETE'],

#     'schema': pod_schema,
#     'datasource': {
#         'default_sort': [('last', -1)],
#     },
#     'versioning': True
# }

# notebooks = {
#     # 'title' tag used in item links. Defaults to the resource title minus
#     # the final, plural 's' (works fine in most cases but not for 'people')
#     # 'item_title': 'p',
#     # by default the standard item entry point is defined as
#     # '/<item_title>/<ObjectId>/'. We leave it untouched, and we also enable an
#     # additional read-only entry point. This way consumers can also perform
#     # GET requests at '/<item_title>/<urlname>/'.
#     'datasource': {
#         'default_sort': [('last', -1)],
#     },
#     # most global settings can be overridden at resource level
#     'resource_methods': ['GET', 'POST'],
#     'item_methods': ['GET', 'PUT', 'PATCH', 'DELETE'],

#     'schema': notebook_schema,
#     'allow_unknown': True
# }

# data = {
#     # most global settings can be overridden at resource level
#     'url': 'data',
#     'resource_methods': ['GET', 'POST'],
#     'item_methods': ['GET', 'PATCH'],
#     'schema': data_schema,
#     'datasource': {
#         'default_sort': [('t', -1)],
#     },
#     # 'embedded_fields': ['pod', 'sensor'],
#     'cache_control': 'max-age=10,must-revalidate',
#     'cache_expires': 10,
# }

# status = {
#     'url': 'pods/status',
#     'item_lookup_field': 'name',
#     'item_url': 'regex("([\w]+\-){1,3}[0-9]{2,4}")',
#     'resource_methods': ['GET'],
#     'item_methods': ['GET', 'PATCH'],
#     'schema': status_schema,
#     'datasource': {
#         'default_sort': [('last', -1)],
#         'source': 'pods',
#         'projection': {'_id': 1, 'name': 1, 'voltage': 1,
#                        '_updated': 1, 'last': 1,
#                        '_latest_notebook': 1, 'mode': 1, 'pod_id': 1}
#     },
#     'item_title': 'Status',
# }

# users = {
#     # 'title' tag used in item links. Defaults to the resource title minus
#     # the final, plural 's' (works fine in most cases but not for 'people')
#     # 'item_title': 'f',
#     # by default the standard item entry point is defined as
#     # '/<item_title>/<ObjectId>/'. We leave it untouched, and we also enable an
#     # additional read-only entry point. This way consumers can also perform
#     # GET requests at '/<item_title>/<username>/'.

#     # We choose to override global cache-control directives for this resource.
#     'cache_control': '',
#     'cache_expires': 0,

#     # Only allow superusers and admin
#     # 'allowed_roles': ['superuser', 'admin'],

#     # most global settings can be overridden at resource level
#     'resource_methods': ['GET', 'POST'],
#     'schema': user_schema
# }

# sensors = {
#     # 'title' tag used in item links. Defaults to the resource title minus
#     # the final, plural 's' (works fine in most cases but not for 'people')
#     # 'item_title': 'f',
#     # by default the standard item entry point is defined as
#     # '/<item_title>/<ObjectId>/'. We leave it untouched, and we also enable an
#     # additional read-only entry point. This way consumers can also perform
#     # GET requests at '/<item_title>/<lastname>/'.
#     'additional_lookup': {
#         'url': 'regex("[\w]+")',
#         'field': 'sid'
#     },
#     # We choose to override global cache-control directives for this resource.
#     'cache_control': 'max-age=10,must-revalidate',
#     'cache_expires': 10,

#     # most global settings can be overridden at resource level
#     'resource_methods': ['GET', 'POST'],
#     'schema': sensor_schema
# }

# # MESSAGES RESOURCE DOMAINS:
# smssync = {
#     # most global settings can be overridden at resource level
#     'url': 'messages/smssync',
#     'resource_methods': ['GET', 'POST'],
#     'schema': messages_schema,
#     'allow_unknown': True,
#     'datasource': {
#         'default_sort': [('_created', -1)]
#     },
# }

# twilio = {
#     # most global settings can be overridden at resource level
#     'url': 'messages/twilio',
#     'resource_methods': ['GET', 'POST'],
#     'schema': messages_schema,
#     'allow_unknown': True,
#     'additional_lookup': {
#         'url': 'regex("[\w]+")',
#         'field': 'id'
#     },
#     'datasource': {
#         'default_sort': [('_created', -1)]
#     },
# }

# nexmo = {
#     # most global settings can be overridden at resource level
#     'url': 'messages/nexmo',
#     'resource_methods': ['GET', 'POST'],
#     'schema': messages_schema,
#     'allow_unknown': True,
#     'additional_lookup': {
#         'url': 'regex("[\w]+")',
#         'field': 'id'
#     },
#     'datasource': {
#         'default_sort': [('_created', -1)]
#     },
# }

# # -----------------------------------------------------------------------------
# #
# # DOMAIN
# #
# # -----------------------------------------------------------------------------

# DOMAIN = {
#     'status': status,
#     'pods': pods,
#     'users': users,
#     'sensors': sensors,
#     'data': data,
#     'smssync': smssync,
#     'twilio': twilio,
#     'nexmo': nexmo,
#     'notebooks': notebooks
# }
