

class GoogleAPI(object):
    """
    GoogleAPI object for accessing google API functions.

    """
    def __init__(self):
        # Use the current flask app to get app-specific config:
        from flask import current_app as app
        # Initialize this class using the app's Google API Key.
        self.api_key = app.config['GOOGLE_API_KEY']

    def geocode(self, location=None):
        """
        Generate an address dict from a location using Google's geocode API

        :param location: A dict containing a longitude and latitude
                        location['coordinates']['longitude']
                        location['coordinates']['latitude']

        Returns an address dictionary that contains the address fields from
        Google's Geocode API.

        https://maps.googleapis.com/maps/api/geocode/

        Default structure of the address dict is:

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

        """
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

    def tower_locate(self, tower=None):
        """
        Uses the Google Geolocate API to determine the location of a cell tower

        :param tower: A dict containing tower location information

            tower = {
                'locationAreaCode': self.lac(),
                'cellId': self.cell_id(),
                'mobileNetworkCode': self.mnc(),
                'mobileCountryCode': self.mcc()
            }

        Returns a location dictionary for use in other Google API functions

            location = {
                'type': 'Point',
                'coordinates': [
                    -9999,
                    -9999
                ]
            }

        If the Google API does not work, we return the coordinates of Princeton

        """
        import json
        import requests
        baseurl = 'https://www.googleapis.com/geolocation/v1/geolocate?key='
        url = baseurl + api_key
        headers = {'content-type': 'application/json'}
        data = {'cellTowers': towers}
        response = requests.post(
            url,
            data=json.dumps(data),
            headers=headers).json()
        location = {
            'type': 'Point',
            'coordinates': [
                -9999,
                -9999
            ]
        }
        if 'error' not in response:
            location['coordinates'] = [
                response['location']['lng'],
                response['location']['lat']
            ]
            return location
        else:
            location['coordinates'] = [
                -74.6702, 40.3571
            ]
        return location

    def elevation(self, location=None):
        """
        Generate and elevation dict from a location using Google's Elevation
        API

        :param location: A dict containing a longitude and latitude
                        location['coordinates']['longitude']
                        location['coordinates']['latitude']

        Returns an elevation dict with the elevation and resolution from
        Google's Elevation API:
            https://maps.googleapis.com/maps/api/elevation/

        elevation = {
            'elevation': 0,
            'resoltion': 0
        }

        """
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
