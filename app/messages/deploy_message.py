import requests
import json
from requests.auth import HTTPBasicAuth
from . import Message
from ..HMACAuth import compute_signature
from flask import current_app


class DeployMessage(Message):

    def __init__(self, data=None, db=None):
        super(DeployMessage, self).__init__(data=data, db=db)
        self.type = 'deploy'
        self.frame = self.__class__.__name__
        self.format.extend([
            {'name': 'mcc', 'length': 3},
            {'name': 'mnc', 'length': 3},
            {'name': 'lac', 'length': 4},
            {'name': 'cell_id', 'length': 4},
            {'name': 'voltage', 'length': 8},
            {'name': 'n_sensors', 'length': 2},
        ])

    # Deployment message format (numbers are str length, so 2 x nBytes)
    #         2 + 4 + 4 + 4 + 4 + 8 + 8 + 2 = 34           |
    ##############################################################
    # Var:  |FrameId|PodId|MCC|MNC|LAC|CI| V | n_sensors|sID1| ... |sIDn|
    # len:  |  2    | 4   | 4 | 4 | 4 | 8| 8 |    2     | 2  | ... | 2  |
    ##############################################################
    # Hard-coded based on Deployment message format:
    def mcc(self):
        (start, end) = self.get_position('mcc')
        if self.content:
            try:
                return int(self.content[start:end])
            except ValueError as e:
                e.args += ('message content invalid', 'DeployMessage', 'mcc()')
                raise
        else:
            self.status = 'invalid'
            assert 0, "Uh-oh. No message content."

    def mnc(self):
        (start, end) = self.get_position('mnc')
        if self.content:
            try:
                return int(self.content[start:end])
            except ValueError as e:
                self.status = 'invalid'
                e.args += ('message content invalid', 'DeployMessage', 'mnc()')
                raise
        else:
            self.status = 'invalid'
            assert 0, "Uh-oh. No message content."

    def lac(self):
        (start, end) = self.get_position('lac')
        if self.content:
            try:
                return int(self.content[start:end], 16)
            except ValueError as e:
                e.args += ('message content invalid', 'DeployMessage', 'lac()')
                raise
        else:
            self.status = 'invalid'
            assert 0, "Uh-oh. No message content."

    def cell_id(self):
        (start, end) = self.get_position('cell_id')
        if self.content:
            try:
                return int(self.content[start:end], 16)
            except ValueError as e:
                self.status = 'invalid'
                e.args += ('message content invalid',
                           'DeployMessage',
                           'cell_id()')
                raise
        else:
            self.status = 'invalid'
            assert 0, "Uh-oh. No message content."

    def voltage(self):
        import struct
        (start, end) = self.get_position('voltage')
        if self.content and len(self.content) >= end:
            try:
                return struct.unpack(
                    '<f',
                    self.content[start:end].decode('hex'))[0]
            except ValueError as e:
                self.status = 'invalid'
                e.args += ('message content invalid',
                           'DeployMessage',
                           'voltage()')
                raise
        else:
            self.status = 'invalid'
            assert 0, "Uh-oh. No message content."

    def n_sensors(self):
        (start, end) = self.get_position('n_sensors')
        if self.content:
            try:
                return int(self.content[start:end], 16)
            except ValueError as e:
                self.status = 'invalid'
                e.args += ('message content invalid',
                           'DeployMessage',
                           'n_sensors()')
                raise
        else:
            self.status = 'invalid'
            assert 0, "Uh-oh. No message content."

    def parse(self):
        # Start by copying pod data to self.data, since PUT is doc complete
        self.data = {}
        self.status = 'parsed'
        try:
            self.data['name'] = self.pod()['name']
            self.data['imei'] = str(self.pod()['imei'])
            self.data['radio'] = self.pod()['radio']
            self.data['pod_id'] = self.pod()['pod_id']
        except KeyError as e:
            e.args += ('pod data missing fields', 'parse()')
            raise

        # now make sure length is actually correct
        i = self.format_length()

        if len(self.content) < i:
            self.status = 'invalid'
            assert 0, 'message content length=' + str(len(self.content)) + \
                      '. Must be >' + str(i)
            return
        elif len(self.content) != (i + 2*self.n_sensors()):
            self.status = 'invalid'
            assert 0, 'message content length=' + str(len(self.content)) + \
                      '. Must equal ' + str(i + 2*self.n_sensors())
            return

        # sIDs is list of sensor objectIds
        self.data['sids'] = []
        self.data['sensors'] = []
        try:
            for j in range(self.n_sensors()):
                s = self.db['sensors'].find_one(
                    {'sid': int(self.content[i:i+2], 16)})
                self.data['sids'].append(s['sid'])  # $in queries
                self.data['sensors'].append(
                    str(s[current_app.config['ITEM_LOOKUP_FIELD']]))
                i += 2
        except:
            self.status = 'invalid'
            assert 0, 'error reading sensor information from database'
        try:
            self.data['cellTowers'] = {
                'locationAreaCode': self.lac(),
                'cellId': self.cell_id(),
                'mobileNetworkCode': self.mnc(),
                'mobileCountryCode': self.mcc()
            }
        except:
            self.status = 'invalid'
            assert 0, 'error extracting cell information from message content'

        self.data['number'] = self.number
        # Transfer ownership of pod to notebook:
        self.data['owner'] = self.pod()['owner']    # Owner is single user
        # self.data['shared'] = [self.pod()['owner']]  # Shared is a list
        self.data['last'] = self.get_now()
        self.data['voltage'] = self.voltage()

        # Do the GOOGLE Stuff:
        location = self.google_geolocate_api()
        self.data['location'] = location if location \
            else current_app.config['LOCATION']
        elevation = self.google_elevation_api()
        self.data['elevation'] = elevation if elevation \
            else current_app.config['ELEVATION']
        self.data['address'] = self.google_geocoding_api()
        # Make a default pod name based on the location
        self.data['nbk_name'] = self.pod()['name'] + ' data from ' + \
            self.data['address']['locality']['short'] + ', ' + \
            self.data['address']['administrative_area_level_1']['short'] + \
            ' in ' + self.data['address']['country']['short']

    def post(self):
        from bson import json_util
        if not self.status == 'invalid':
            print "posting deploy message"
            headers = {'If-Match': str(self.pod_etag()),
                       'content-type': 'application/json'}
            data = json.dumps(self.data, default=json_util.default)
            url = self.pod_url()
            token = current_app.config['API_AUTH_TOKEN']
            auth = HTTPBasicAuth(
                'api',
                compute_signature(token, url, data))
            d = requests.put(url=url, data=data, headers=headers, auth=auth)
            if d.status_code == 201:
                print "New deployment created"
            else:
                print d.status_code
                print d.text
        else:
            print "Warning: message format is invalid."

    def google_geolocate_api(self):
        api_key = current_app.config['GOOGLE_API_KEY']
        if not api_key:
            assert 0, "Must provide api_key"
        tower = self.data['cellTowers']
        location = {}
        # Assume this doesn't work:
        location['lat'] = 'unknown'
        location['lng'] = 'unknown'
        location['accuracy'] = 'unknown'

        url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' \
            + api_key
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

    def google_elevation_api(self):
        loc = self.data['location']
        api_key = current_app.config['GOOGLE_API_KEY']
        if not api_key:
            assert 0, "Must provide api_key"
        if 'unknown' not in loc.values():
            baseurl = 'https://maps.googleapis.com/' + \
                      'maps/api/elevation/json?' + \
                      'locations='
            tailurl = '&sensor=false&key=' + api_key
            url = baseurl + str(loc['lat']) + \
                ',' + str(loc['lng']) + tailurl
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

    def google_geocoding_api(self):
        api_key = current_app.config['GOOGLE_API_KEY']
        loc = self.data['location']
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
            baseurl = 'https://maps.googleapis.com/maps/' + \
                      'api/geocode/json?latlng='
            tailurl = '&sensor=false&key=' + api_key
            url = baseurl + str(loc['lat']) + ',' + str(loc['lng']) + tailurl
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
