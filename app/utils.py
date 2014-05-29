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


def pod_name():
    return choice(firstnames) + '-' + choice(lastnames) + \
        '-' + str(randint(1000, 9999))


def compute_signature(token, uri, data):
        """Compute the signature for a given request

        :param uri: full URI for request on API
        :param params: post vars sent with the request
        :returns: The computed signature
        """
        s = uri.split('://')[1]
        if data:
            if type(data) is dict:
                d = sorted(data, key=data.get)
                for k in d:
                    s += k + d[k]
            if type(data) is str:
                s += data

        # compute signature and compare signatures
        mac = hmac.new(token, s.encode("utf-8"), sha1)
        computed = base64.b64encode(mac.digest())
        # print computed.strip()
        return computed.strip()


##############################################
# PARSING UTILITIES                          #
##############################################
def make_pod_id():
    pods = app.extensions['pymongo']['MONGO'][1]['pods']
    return (pods.find().sort('pod_id', -1)[0]['pod_id'] + 1)


def get_now():
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())


def get_time(content, i):
    # parse unixtime to long int, then convert to database time
    try:
        unixtime = struct.unpack('<L', content[i:i+8].decode('hex'))[0]
    except:
        raise InvalidMessageException(
            'Error decoding timestamp',
            status_code=400)
    t = time.gmtime(unixtime)
    # dbtime is (e.g.) "Tue, 17 Sep 2013 01:33:56 GMT"
    dbtime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", t)
    return dbtime


def get_value(content, i, sensor):
    # parse value based on format string
    try:
        value = struct.unpack(
            str(sensor['byteorder'] + sensor['fmt']),
            content[i:i+(2*int(sensor['nbytes']))].decode('hex'))[0]
    except:
        raise InvalidMessageException(
            'Error parsing format string',
            status_code=400)

    # Right here we would do some initial QA/QC based on whatever
    # QA/QC limits we eventually add to the sensor specifications.
    # Not returning the flag yet.
    qa_qc(sensor, value)
    return float(value)


def qa_qc(sensor, value):
    pass


def google_geolocate_api(tower, api_key):
    if not api_key:
        assert 0, "Must provide api_key"

    location = {}
    # Assume this doesn't work:
    location['lat'] = 'unknown'
    location['lng'] = 'unknown'
    location['accuracy'] = 'unknown'

    url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' + api_key
    headers = {'content-type': 'application/json'}
    data = {'cellTowers': [{
        'cellId': tower['cellId'],
        'locationAreaCode':tower['locationAreaCode'],
        'mobileCountryCode':tower['mobileCountryCode'],
        'mobileNetworkCode':tower['mobileNetworkCode']
        }]}
    response = requests.post(
        url,
        data=json.dumps(data),
        headers=headers).json()
    if 'error' not in response:
        location['lat'] = response['location']['lat']
        location['lng'] = response['location']['lng']
        location['accuracy'] = response['accuracy']
        return location
    else:
        print response
        return 0


def google_elevation_api(loc, api_key=None):
    if not api_key:
        assert 0, "Must provide api_key"
    if 'unknown' not in loc.values():
        baseurl = 'https://maps.googleapis.com/maps/api/elevation/json?' + \
                  'locations='
        tailurl = '&sensor=false&key=' + api_key
        url = baseurl + str(loc['lat']) + ',' + str(loc['lng']) + tailurl
        response = requests.get(url).json()
        if response['status'] == 'OK':
            return {
                'elevation': response['results'][0]['elevation'],
                'resolution': response['results'][0]['resolution']
            }
        else:
            return 0
    else:
        return 0


def google_geocoding_api(loc, api_key=None):
    if not api_key:
        assert 0, "Must provide api_key"
    # must pre-seed this with all the data we want shorted:
    address = {
        'country': {'short': 'unknown', 'full': 'unknown'},
        'locality': {'short': 'unknown', 'full': 'unknown'},
        'administrative_area_level_1': {
            'short': 'unknown',
            'full': 'unknown'},
        'administrative_area_level_2': {
            'short': 'unknown',
            'full': 'unknown'},
        'administrative_area_level_3': {
            'short': 'unknown',
            'full': 'unknown'},
        'route': {'short': 'unknown', 'full': 'unknown'},
        'street_address': {'short': 'unknown', 'full': 'unknown'},
    }
    if 'unknown' not in loc.values():
        baseurl = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='
        tailurl = '&sensor=false&key=' + api_key
        url = baseurl + str(loc['lat']) + ',' + str(loc['lng']) + tailurl
        response = requests.get(url).json()
        if response['status'] == 'OK':
            address['formatted_address'] = \
                response['results'][0]['formatted_address']
            for result in response['results']:
                for address_component in result['address_components']:
                    if address_component['types'][0] in address and \
                            'short' in address[address_component['types'][0]]:
                        address[address_component['types'][0]]['full'] = \
                            str(address_component['long_name'])
                        address[address_component['types'][0]]['short'] = \
                            str(address_component['short_name'])
                    else:
                        address[address_component['types'][0]] = \
                            str(address_component['long_name'])
    return address
