import struct
import json
import time
from flask import current_app as app
import requests
from random import choice, randint
from names import firstnames, lastnames
from hashlib import sha1
import base64
import hmac


# Definie a exception class to report errors (handy for debugging)
class InvalidMessageException(Exception):
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
