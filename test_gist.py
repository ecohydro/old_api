import os
import base64
import hmac
import time
from hashlib import sha1
import requests
import json
from requests.auth import HTTPBasicAuth

# BEGIN SECURITY/SENSITIVE CODE #
# Read in any local environment variables stored in a .env file
# NOTE: DO NOT UPLOAD ANY .ENV FILE TO GITHUB. EVER.
if os.path.exists('.env'):
    print('Importing environment variables from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]
# You must set the API_AUTH_TOKEN in the environment.
# NOTE: DO NOT PUT THE API_AUTH_TOKEN INTO THIS CODE. EVER.
API_AUTH_TOKEN = os.environ.get('API_AUTH_TOKEN')
# END SECURITY/SENSITIVE CODE #

# Define the API parameters. These are public and knowable.
SERVER_NAME = 'api.pulsepod.io'
API_URL = 'https://' + SERVER_NAME

# Here's a reasonable data packet to use that will throw a 400 error:
invalid_data = {
    'item': 'value',
    'item2': 'value2'
}

# A minimum valid data object contains:
# a float value
# a GEOJSON point location
valid_data = {
    'v': 10.0,
    'loc': {
        'type': 'Point',
        'coordinates': [-106.834121, 34.42957]
    },
    's': '55cce09f13e09a006500000c',  # We expect an db object id now.
    'pod': '55cce07a13e09a005d00000f',  # We expect a db object id now.
    't': time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
}


# This is the code we use to compute signatures to validate
# API post requests. It requires the API token, the post URI, and
# The complete data string or dict being sent to the API.
# This code can be shared publically without compromising our security.
def compute_signature(token, uri, data):
        """Compute the signature for a given request

        :param uri: full URI for request on API
        :param params: post vars sent with the request
        :returns: The computed signature

        """
        s = uri.split('://')[1]  # Avoid hiccups related to http/https
        if data:
            if type(data) is dict:  # We need to sort the dict for consistency
                d = sorted(data, key=data.get)
                for k in d:
                    s += k + d[k]
            if type(data) is str:  # Otherwise, just use the string as is.
                s += data
        # compute signature and compare signatures
        mac = hmac.new(token, s.encode("utf-8"), sha1)  # Hash it up.
        computed = base64.b64encode(mac.digest())
        return computed.strip()  # Return the hashed signature.

# Setup the config dictionary.
config = {}
config['API_URL'] = API_URL
config['API_AUTH_TOKEN'] = API_AUTH_TOKEN


def post_data(data=None, config=None):
    # Set headers for this request.
    headers = {'Content-Type': 'application/json'}
    # Compute the signature for this POST request
    try:
        user = 'test_pod'  # We don't check this. There is no pod user.
        url = config['API_URL'] + '/data'   # POST to the data resource
        '''
        We use HTTPBasicAuth to generate an authentication string. The
        authentication string is simply a base64 string composed of a user and
        a password, seperated by a ':'. Details can be found here:
            https://en.wikipedia.org/wiki/Basic_access_authentication

        To provide request-specific security, we do the following:
            1. We ignore the user component. This is a dummy string and can be
            anything. The reason is because we don't want pods to have
            usernames that correspond to anything in our database. That would
            open up a method of attack if the pod username was ever in the
            clear.

            2. The 'password' is generated using the compute_signature
            function. This function creates a unique signature using the
            contents of the JSON data contained in the request. We use the
            API_AUTH_TOKEN to generate this hash.

            3. On the API, we use the post request data to re-create the hash
            and compare the result to the value of the password supplied in the
            Authentication header. If the hashes match, we can be certain that
            the sender of the POST request had access to the API_AUTH_TOKEN.
        '''
        # Create the authentication header:
        auth = HTTPBasicAuth(
            user,
            compute_signature(
                config['API_AUTH_TOKEN'],
                url,
                json.dumps(data)))
    except KeyError as e:  # Did we provide all the config needed?
        e.args += ('Missing', 'config')
        raise
    except TypeError as e:  # Was the config value set properly?
        e.args += ('Invalid or None', 'in config')
        raise
    # At this point, we have a valid auth.
    # If we have data, then make a POST request.
    if data:
        r = requests.post(
            url,
            data=json.dumps(data),
            headers=headers,
            auth=auth
        )
        if r.json():
            print r.json()
            return r.json()  # Return the API's result
        else:
            return "Unknown error in POST request to API"
    else:
        assert 0, \
            "No message data provided."

'''
TO USE THIS CODE:

> from test_gist import post_data, config, invalid_data, valid_data

'''
