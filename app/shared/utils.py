from hashlib import sha1
import base64
import hmac
from flask import current_app as app
from twilio.rest import TwilioRestClient
import phonenumbers


def send_message(number=None, content=None):
    if number is None:
        assert 0, "Must provide number"
    z = phonenumbers.parse(number, None)
    if not phonenumbers.is_valid_number(z):
        assert 0, "Dodgy number."
    if content is None:
        assert 0, "Message content is empty"
    account = app.config['TWILIO_ACCOUNT_SID']
    token = app.config['TWILIO_AUTH_TOKEN']
    client = TwilioRestClient(account, token)
    message = client.messages.create(
        to=number,
        from_=app.config['TWILIO_NUMBER'],
        body=content)
    return message


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
        return computed.strip()


class GoogleAPI:
    # Use the current flask app to get app-specific config:
    from flask import current_app as app

    def __init__(self):
        # Initialize this class using the app's Google API Key.
        self.api_key = app.config['GOOGLE_API_KEY']

    def geocoding(self, location):
        import requests
        if location is None:
            assert 0, "Must provide a location value (GeoJSON point)." + \
                      " Did you mean to call google_geolocate_api() first?"
        if not self.api_key:
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
        if -9999 not in location['coordinates']:
            baseurl = 'https://maps.googleapis.com/maps/' + \
                      'api/geocode/json?latlng='
            tailurl = '&sensor=false&key=' + self.api_key
            lng = str(location['coordinates'][0])
            lat = str(location['coordinates'][1])
            url = baseurl + lat + ',' + lng + tailurl
            response = requests.get(url).json()
            if response['status'] == 'OK':
                address['formatted_address'] = \
                    response['results'][0]['formatted_address']
                for result in response['results']:
                    for address_component in result['address_components']:
                        if address_component['types'][0] in address and \
                                'short' in \
                                address[address_component['types'][0]]:
                            address[address_component['types'][0]]['full'] = \
                                str(address_component['long_name'])
                            address[address_component['types'][0]]['short'] = \
                                str(address_component['short_name'])
                        else:
                            address[address_component['types'][0]] = \
                                str(address_component['long_name'])
        return address

    def elevation(self, location=None):
        import requests
        if location is None:
            assert 0, "Must provide a location value (GeoJSON point)." + \
                      " Did you mean to call google_geolocate_api() first?"
        if not self.api_key:
            assert 0, "Must provide api_key"
        if -9999 not in location['coordinates']:
            baseurl = 'https://maps.googleapis.com/' + \
                      'maps/api/elevation/json?' + \
                      'locations='
            tailurl = '&sensor=false&key=' + self.api_key
            lng = str(location['coordinates'][0])
            lat = str(location['coordinates'][1])
            url = baseurl + lat + ',' + lng + tailurl
            response = requests.get(url).json()
            if response['status'] == 'OK':
                return {
                    'elevation': response['results'][0]['elevation'],
                    'resolution': response['results'][0]['resolution']
                }
            else:
                return {
                    'elevation': 0,
                    'resolution': 0
                }
        else:
            return 0


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
