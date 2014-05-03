from eve import Eve
from flask import request
from eve.auth import HMACAuth
from hashlib import sha1
import base64
import hmac
import os
from hashlib import sha1
from compat import izip
from utils import InvalidMessage
from collections import OrderedDict
from basicauth import decode
from flask import current_app as app

class HMACAuth(HMACAuth):

    def __init__(self,token=None):
        if token:
            self.token = token
        else:
            self.token = os.getenv('API_AUTH_TOKEN')
       
    def compute_signature(self, uri, data):
        """Compute the signature for a given request

        :param uri: full URI for request on API
        :param params: post vars sent with the request
        
        :returns: The computed signature
        """
        s = uri
        print data
        if len(data) > 0:
            #d = OrderedDict(sorted(data.items(), key=lambda x: x[1]))
            #for k in d:
            s += data #k + d[k]

        # compute signature and compare signatures
        print s
        mac = hmac.new(self.token, s.encode("utf-8"), sha1)
        computed = base64.b64encode(mac.digest())
        print computed.strip()
        return computed.strip()

    def check_auth(self, userid, uri, data, hmac_hash, resource, method):
        if method in ['HEAD','OPTIONS']: # Let it rain.
            return True
        elif method in ['GET']: #Stub for user-level auth methods
            return True
        else: # Everything else requires API-ninja access
            return self.validate(uri, data, hmac_hash)

    def validate(self, uri, data, signature):
        """Validate a request from Twilio

        :param uri: full URI that was requested on your server
        :param params: post vars that were sent with the request
        :param signature: expexcted signature in HTTP Authorization header
        :param auth: tuple with (account_sid, token)

        :returns: True if the request passes validation, False if not
        """
        return secure_compare(self.compute_signature(uri, data), signature)

    def authorized(self, allowed_roles, resource, method):
        """ Validates the the current request is allowed to pass through.

        :param allowed_roles: allowed roles for the current request, can be a
                              string or a list of roles.
        :param resource: resource being requested.
        """
  
        try:
            userid, hmac_hash = decode(request.headers.get('Authorization'))
        except:
            userid = None
            hmac_hash = None

        return self.check_auth(userid, request.url, request.get_data(), \
                            hmac_hash, resource, method )


def secure_compare(string1, string2):
    """Compare two strings while protecting against timing attacks

    :param str string1: the first string
    :param str string2: the second string

    :returns: True if the strings are equal, False if not
    :rtype: :obj:`bool`
    """
    if len(string1) != len(string2):
        return False
    result = True
    for c1, c2 in izip(string1, string2):
        result &= c1 == c2
    return result
