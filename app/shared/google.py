

class GoogleAPI:

    def __init__(self):
        # Use the current flask app to get app-specific config:
        from flask import current_app as app
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
