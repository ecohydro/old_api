import time
import json
import requests
from app.shared.utils import compute_signature
from requests.auth import HTTPBasicAuth
import phonenumbers
from flask import current_app as app


def format_number_E164(number, country=None):
    return phonenumbers.format_number(
        phonenumbers.parse(number, country),
        phonenumbers.PhoneNumberFormat.E164)


class SMS(object):

    def __init__(self, message_id=None, resource=None, data=None):
        """
        >>> A = SMS()
        >>> A.__class__
        <class 'app.sms.SMS.SMS'>
        >>> A.__class__.__name__
        'SMS'
        >>> A = SMS(message_id='this_id')
        >>> A._id
        'this_id'
        >>> A = SMS(data='this_data')
        >>> A.data
        'this_data'
        """

        self.message_id = message_id if message_id else None
        self.data = data if data else None
        self._keep = ['status', 'source', 'number',
                      'time_stamp', 'message_content', 'message_id']

    @staticmethod
    def create(resource=None, message_id=None, data=None):
        """
        Calling create without arguments won't work:
        >>> SMS.create()
        Traceback (most recent call last):
            ...
        AssertionError: Must provide resource

        Calling without a valid resource won't work:
        >>> SMS.create(resource='None')
        Traceback (most recent call last):
            ...
        AssertionError: Bad SMS creation: None
        """

        if resource is None:
            assert False, "Must provide resource"

        if resource is "twilio":
            if message_id:
                return Twilio(
                    message_id=message_id,
                    data=data)
            else:
                assert 0, "Twilio requires message Id"
        if resource == "smssync":
            return SMSSync(
                data=data,
                message_id=message_id
            )
        assert 0, "Bad SMS creation: " + resource

    def clean(self):
        try:
            # Clean out the garbage from the API responses:
            for key in self.data.keys():
                if key not in self._keep:
                    self.data.pop(key)
        except AttributeError as e:
            e.args += ('SMS.data must be a dict to remove invalid keys',
                       'SMS.clean()')
            raise

    def get(self):
        raise NotImplementedError('Define get(self) for all SMS subclasses')

    def post(self):
        with app.app_context():
            headers = {'Content-Type': 'application/json'}
            try:
                # user = 'gateway' if not self.config['TESTING'] else 'test'
                user = 'gateway'
                url = app.config['API_URL'] + '/messages/' + self.resource()
                auth = HTTPBasicAuth(
                    user,
                    compute_signature(
                        app.config['API_AUTH_TOKEN'],
                        url,
                        json.dumps(self.data)))
            except KeyError as e:
                e.args += ('Missing', 'in app.config')
                raise
            except TypeError as e:
                e.args += ('Invalid or None', 'in app.config')
                raise
            if self.data and not self.resource() == 'sms':
                r = requests.post(
                    url,
                    data=json.dumps(self.data),
                    headers=headers,
                    auth=auth
                )
                if r.json():
                    return r.json()
                else:
                    return "Unknown error in POST request to API"
            else:
                assert 0, \
                    "No message data provided. Call SMS.get(), then SMS.post()"

    def resource(self):
        return str(self.__class__.__name__).lower()


class Twilio(SMS):

    def __init__(self, message_id=None, resource=None, data=None, config=None):
        super(Twilio, self).__init__(
            message_id=message_id,
            resource=resource,
            data=data)
        # We are only keeping the fields we need. Note that field names
        # correspond to db_field names, and not mongoengine class properties.
        # consult the message class in the models folder to sort this out.
        self._keep = ['status', 'source', 'number',  # not message_id
                      'time_stamp', 'message', 'mid']  # not messge_content

    def get(self):
        with app.app_context():
            mime = '.json'
            try:
                auth = HTTPBasicAuth(app.config['TWILIO_ACCOUNT_SID'],
                                     app.config['TWILIO_AUTH_TOKEN'])
                # URL looks like:
                # https://api.twilio.com/2010-04-01/Accounts/USR/Messages/MSG.json
                url = app.config['TWILIO_URL'] + \
                    app.config['TWILIO_ACCOUNT_SID'] + \
                    '/Messages/' + self.message_id + mime
            except KeyError as e:
                e.args += ('Missing', 'in app.config')
                raise
            except TypeError as e:
                e.args += ('Invalid or None', 'in app.config')
                raise
            if app.config['TWILIO_ACCOUNT_SID'] \
                    and app.config['TWILIO_AUTH_TOKEN']:
                r = requests.get(url=url, auth=auth)
                if r.raise_for_status():
                    r.raise_for_status()
                else:
                    self.data = r.json()
                    self.data['status'] = 'queued'
                    self.data['source'] = 'twilio'
                    self.data['number'] = format_number_E164(self.data['from'])
                    self.data['time_stamp'] = time.strftime(
                        "%a, %d %b %Y %H:%M:%S GMT",
                        time.gmtime())
                    # We are setting these fields to match the db_fields and
                    # not the mongoengine class properties. Consult the
                    # message class definition for more details.
                    self.data['message'] = self.data['body']
                    self.data['mid'] = self.data['sid']
            else:
                assert 0, "No Twilio Auth provided in app.config"


class SMSSync(SMS):

    def __init__(self, message_id=None, resource=None, data=None):
        super(SMSSync, self).__init__(
            resource=resource,
            message_id=message_id,
            data=data)
        # We are only keeping the fields we need. Note that field names
        # correspond to db_field names, and not mongoengine class properties.
        # consult the message class in the models folder to sort this out.
        self._keep = ['status', 'source', 'number',
                      'time_stamp', 'message', 'mid']

    def get(self):

        self.data['time_stamp'] = time.strftime(
            "%a, %d %b %Y %H:%M:%S GMT",
            time.gmtime())
        self.data['status'] = 'queued'
        self.data['source'] = 'smssync'
        try:
            self.data['number'] = format_number_E164(self.data['from'])
        except:
            self.data['number'] = self.data['from']
        # Use the db field name instead of the mongoengine field name:
        self.data['mid'] = self.data['message_id']

    def post(self):
        with app.app_context():
            url = app.config['API_URL'] + '/messages/' + 'smssync'
            data = json.dumps(self.data)
            print data
            headers = {'Content-Type': 'application/json'}
            auth = HTTPBasicAuth(
                'gateway',
                compute_signature(
                    app.config['API_AUTH_TOKEN'],
                    url,
                    data))
        r = requests.post(url, data=data, headers=headers, auth=auth)
        print r.json()
        return r.raise_for_status() if r.raise_for_status() else r.json()
