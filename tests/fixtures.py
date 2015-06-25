from werkzeug.datastructures import ImmutableMultiDict
import os


class GenericTestData(object):

    def __init__(self):
        self.message_id = 'test_id'
        self.data = 'asd123qsda'
        self._bad_id = 'thisisabadid'


class TwilioTestData(GenericTestData):

    def __init__(self):
        super(TwilioTestData, self).__init__()
        self.message_id = 'SM06a3af96e000513010cf36dbe4faa4d5'
        self.auth = str(os.getenv('TWILIO_AUTH_TOKEN')).replace("'", "")
        self.twilio_url = str(os.getenv('TWILIO_POST_URL')).replace("'", "")
        self.data = ImmutableMultiDict([
            ('ToCity', u'CHICAGO'),
            ('MessageSid', u'SMc976f526a10a80ae45a78a3cb0aaa082'),
            ('ApiVersion', u'2010-04-01'), ('From', u'+16096584015'),
            ('FromZip', u'08505'),
            ('SmsMessageSid', u'SMc976f526a10a80ae45a78a3cb0aaa082'),
            ('SmsStatus', u'received'),
            ('ToZip', u'60614'),
            ('FromCity', u'TRENTON'),
            ('FromCountry', u'US'),
            ('Body', u'PulsePod Test Message'),
            ('ToState', u'IL'),
            ('FromState', u'NJ'),
            ('AccountSid', u'AC9e12014f360e61a601de59b5ad4fcfcf'),
            ('ToCountry', u'US'),
            ('To', u'+13122290504'),
            ('SmsSid', u'SMc976f526a10a80ae45a78a3cb0aaa082'),
            ('NumMedia', u'0')])
        self.data_no_message_id = ImmutableMultiDict([
            ('ToCity', u'CHICAGO'),
            ('ApiVersion', u'2010-04-01'),
            ('From', u'+16096584015'),
            ('FromZip', u'08505'),
            ('SmsMessageSid', u'SMc976f526a10a80ae45a78a3cb0aaa082'),
            ('SmsStatus', u'received'),
            ('ToZip', u'60614'),
            ('FromCity', u'TRENTON'),
            ('FromCountry', u'US'),
            ('Body', u'PulsePod Test Message'),
            ('ToState', u'IL'),
            ('FromState', u'NJ'),
            ('AccountSid', u'AC9e12014f360e61a601de59b5ad4fcfcf'),
            ('ToCountry', u'US'), ('To', u'+13122290504'),
            ('SmsSid', u'SMc976f526a10a80ae45a78a3cb0aaa082'),
            ('NumMedia', u'0')])
#       self.signature = 'srtwn2MvnsQbQIKvnYN0Jh8KxR8='
        self.signature = 'Ov9mbQV/fC06yEZM+lu2FwFIq+Q='


class SMSSyncTestData(GenericTestData):

    def __init__(self):
        super(SMSSyncTestData, self).__init__()


class GenericMessageFixture(object):

    def __init__(self):
        self._id = 'test_id'
        self.data = 'asd123qsda'
        self._bad_id = 'thisisabadid'


class InvalidMessageFixture(GenericMessageFixture):

    def __init__(self):
        super(GenericMessageFixture, self).__init__()
        self.url = 'https://api.pulsepod.io/messages/' + \
            'twilio/5357d106c081c500027fe178'
        self.data = {
            u'status': u'queued',
            u'_updated': u'Sun, 04 May 2014 21:19:22 GMT',
            u'number': u'16096584015',
            u'_etag': u'b7307b5024596df243c4f8c17ab92d5035aecf47',
            u'nobs': 0, u'source': u'twilio',
            u'_links': {
                u'self': {
                    u'href': u'api.pulsepod.io/messages/twilio/' +
                        '\5357d106c081c500027fe178',
                    u'title': u'Twilio'},
                u'collection': {
                    u'href':
                    u'api.pulsepod.io/messages/twilio',
                    u'title': u'messages/twilio'},
                u'parent': {
                    u'href': u'api.pulsepod.io',
                    u'title': u'home'}},
            u't': u'Wed, 23 Apr 2014 14:41:10 GMT',
            u'nposted': 0,
            u'_created': u'Wed, 23 Apr 2014 14:41:10 GMT',
            u'message': u'Test', u'_id':
            u'5357d106c081c500027fe178', u'type': u'invalid',
            u'id': u'SM25bbc5e0fbc16d9596627d3e8d85a12f'
        }


class DeployMessageFixture(GenericMessageFixture):

    def __init__(self):
        super(GenericMessageFixture, self).__init__()
        self.url = 'https://api.pulsepod.io/messages/' + \
            'twilio/539a281da8af0f0002aec782'
        self.data = {
            u'status': u'queued',
            u'_updated': u'Thu, 17 Apr 2014 16:08:57 GMT',
            u'number': u'16096587658',
            u'id': u'aae16019',
            u'nobs': 0,
            u'source': u'twilio',
            u'_links': {
                u'self': {
                    u'href': u'api.pulsepod.io/messages/' +
                    'twilio/539a281da8af0f0002aec782',
                    u'title': u'Twilio'},
                u'parent': {
                    u'href': u'api.pulsepod.io',
                    u'title': u'home'},
                u'collection': {
                    u'href': u'api.pulsepod.io.com/messages/twilio',
                    u'title': u'messages/twilio'}},
            u'nposted': 0,
            u'_created': u'Thu, 17 Apr 2014 16:08:56 GMT',
            u'message':
                u'030015310026873c77e34072481502F8FC',
            u'_id': u'539a281da8af0f0002aec782',
            u'type': u'unknown',
            u'_etag': u'6282a68b7df3bac3f3561e606d43cc9885a220a6'
        }


class DataMessageFixture(GenericMessageFixture):

    def __init__(self):
        super(GenericMessageFixture, self).__init__()
        self.url = 'https://api.pulsepod.io/messages/' + \
            'twilio/52d07ba1b3ca080002ac23af'
        self.data = {
            u'_updated': u'Sun, 12 Jan 2014 01:34:07 GMT',
            u'status': u'queued',
            u'number': u'14154817671',
            u'_etag': u'2ea52d1479212b458bfe0efcb4213cc30e37d8a4',
            u'source': u'twilio',
            u'_links': {
                u'self': {
                    u'href': u'api.pulsepod.io/messages/' +
                    'twilio/52d07ba1b3ca080002ac23af',
                    u'title': u'Twilio'},
                u'parent': {
                    u'href': u'api.pulsepod.io',
                    u'title': u'home'},
                u'collection': {
                    u'href': u'api.pulsepod.io/messages/twilio',
                    u'title': u'messages/twilio'}},
            u't': u'Thu, 12 Jun 2014 22:22:21 GMT',
            u'_created': u'Thu, 12 Jun 2014 22:22:21 GMT',
            u'message':
                u'0007026874D0524E62283D707BD052E8FB293D08' +
                '03606DD052F4FD54396874D052B172283D707BD0520F2D2A3D',
            u'_id': u'52d07ba1b3ca080002ac23af',
            u'id': u'SM0cb492da98f575450b8af28afe1b133c'
        }


class TestPodFixture(object):

    def __init__(self):
        self.data = {
            '_created': 'ISODate("2014-04-18T19:39:51Z")',
            '_id': 'ObjectId("53517f8799e3b0df46a18912")',
            '_notebook': 1,
            '_updated': 'ISODate("2014-04-18T19:39:51Z")',
            'firmware': 0,
            'imei': '0000000000000000',
            'mode': 'inactive',
            'name': 'Test-Pod-0001',
            'nbk_name': "Test-Pod-0001's Default Notebook",
            'number': '18005551212',
            'owner': 'pulsepod',
            'pod_id': 1,
            'qr': 'https://s3.amazonaws.com/pulsepodqrsvgs/Test-Pod-0001.svg',
            'radio': "gsm",
            'shared': ["pulsepod"],
            'status': "born",
            'tags': ["none"],
            'voltage': 0
        }
