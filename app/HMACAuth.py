from flask import request, current_app
from eve.auth import HMACAuth
import os
from compat import izip
from basicauth import decode
from shared.utils import compute_signature


class HMACAuth(HMACAuth):

    def __init__(self, token=None):
        if token:
            self.token = token
        else:
            self.token = os.getenv('API_AUTH_TOKEN')

    def check_auth(self, userid, uri, data, hmac_hash, resource, method):
        if method in ['HEAD', 'OPTIONS']:  # Let it rain.
            return True
        elif method in ['GET']:  # Stub for user-level auth methods
            return self.validate_api_access(uri, data, resource)
        else:  # Everything else requires API-ninja access
            return self.validate(uri, data, hmac_hash)

    def validate_api_access(self, uri, data, resource):
        """ Validate a GET request to the API

        :param uri: full URI that was requested on the server

        """
        api_key = None
        if request.headers.get('Authorization'):
            try:
                api_key, password = decode(
                    request.headers.get('Authorization')
                )
            except AttributeError:
                return False
        if api_key:
            user = current_app.data.models['user'].objects(
                api_key=api_key
            ).first()
        else:
            return False
        if user:
            current_app.logger.debug(
                "%s found with key %s!" % (user.username, api_key)
            )
            resource_config = current_app.config['DOMAIN'][resource]
            if len(resource_config['allowed_roles']) > 0:
                if user.role in resource_config['allowed_roles']:
                    return user
                else:
                    return False
            return user
        else:
            return False

    def validate(self, uri, data, signature):
        """Validate a request to the API

        :param uri: full URI that was requested on your server
        :param params: post vars that were sent with the request
        :param signature: expexcted signature in HTTP Authorization header
        :param auth: tuple with (account_sid, token)

        :returns: True if the request passes validation, False if not
        """
        return secure_compare(str(compute_signature(self.token, uri, data)),
                              str(signature))

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
        return self.check_auth(userid, request.url, request.get_data(),
                               hmac_hash, resource, method)


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
