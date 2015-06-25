import pea
import os
import json
from app import create_app
from flask.ext.pymongo import MongoClient
from app.shared import models

known_users = 2
known_data = 10
known_messages = 10
known_notebooks = 10
known_pods = 10
known_sensors = 10


def close_pymongo_connection(app):
    """
    Close the pymongo connection in the PulsePod API
    """
    if 'pymongo' not in app.extensions:
        return
    del app.extensions['pymongo']['MONGO']
    del app.media


def close_mongoengine_connection(app):
    """
    Close the mongoengine connection in the PulsePod API
    """
    if 'mongoengine' not in app.extensions:
        return
    del app.extensions['mongoengine']


class TestMinimal(pea.TestCase):
    """ Start the building of the tests for the PulsePod API
    by subclassing this class and provide proper settings
    using :func:`setUp()`
    """
    def setUp(self, config=None):
            """ Prepare the test fixture

            :param config: the name of the config class.  Defaults
                                  to `testing`.
            """
            super(TestMinimal, self).setUp()
            self.this_directory = os.path.dirname(os.path.realpath(__file__))
            if config is None:
                config = 'testing'
            elif config in ('production', 'development', 'heroku'):
                assert 0, "Unable to run tests with %s config" % config
            self.connection = None
            self.app = create_app('testing')
            self.app_context = self.app.app_context()
            self.app_context.push()
            self.setupDB()
            self.test_client = self.app.test_client()
            self.domain = self.app.config['DOMAIN']
            self.config = self.app.config
            self.DataMessage = {
                'message_content': u'020f5be1018446df5314512d41b6028446df5' +
                '339ecb6427438df53cee69f4255038446df538dc656427438df530dbe' +
                '9442642adf53011aa641'
            }
            self.DeployMessage = {
                'message_content': u'030f5b310026032229c58b436b4003e1b655'
            }

    def tearDown(self):
        super(TestMinimal, self).tearDown()
        self.dropDB()
        self.app_context.pop()
        del self.app

    def assert200(self, status):
        self.assertEqual(status, 200)

    def assert201(self, status):
        self.assertEqual(status, 201)

    def assert301(self, status):
        self.assertEqual(status, 301)

    def assert404(self, status):
        self.assertEqual(status, 404)

    def assert304(self, status):
        self.assertEqual(status, 304)

    def get(self, resource, query='', item=None, headers=None):
        if resource in self.domain:
            resource = self.domain[resource]['url']
        if item:
            request = '/%s/%s%s' % (resource, item, query)
        else:
            request = '/%s%s' % (resource, query)

        r = self.test_client.get(request)
        return self.parse_response(r)

    def post(self, url, data, headers=None, content_type='application/json'):
        if headers is None:
            headers = []
        headers.append(('Content-Type', content_type))
        r = self.test_client.post(url, data=json.dumps(data), headers=headers)
        return self.parse_response(r)

    def put(self, url, data, headers=None):
        if headers is None:
            headers = []
        headers.append(('Content-Type', 'application/json'))
        r = self.test_client.put(url, data=json.dumps(data), headers=headers)
        return self.parse_response(r)

    def patch(self, url, data, headers=None):
        if headers is None:
            headers = []
        headers.append(('Content-Type', 'application/json'))
        r = self.test_client.patch(url, data=json.dumps(data), headers=headers)
        return self.parse_response(r)

    def delete(self, url, headers=None):
        r = self.test_client.delete(url, headers=headers)
        return self.parse_response(r)

    def bulk_insert(self):
        pass

    def parse_response(self, r):
        try:
            v = json.loads(r.get_data())
        except json.JSONDecodeError:
            v = None
        return v, r.status_code

    def setupDB(self):
        settings = self.app.config['MONGODB_SETTINGS']
        self.connection = MongoClient(settings['HOST'],
                                      settings['PORT'])
        self.connection.drop_database(settings['DB'])
        if 'USERNAME' in settings:
            self.connection[settings['DB']].add_user(
                settings['USERNAME'], settings['PASSWORD'])
        self.Pod = models.Pod
        self.User = models.User
        self.Message = models.Message
        self.Notebook = models.Notebook
        self.Sensor = models.Sensor
        self.Data = models.Data
        self.bulk_insert()

    def dropDB(self):
        settings = self.app.config['MONGODB_SETTINGS']
        self.connection = MongoClient(
            settings['HOST'],
            settings['PORT'])
        self.connection.drop_database(settings['DB'])
        self.connection.close()


class TestBase(TestMinimal):

    def setUp(self):
        super(TestBase, self).setUp()
        self.pymongo = self.app.extensions['pymongo']['PYMONGO'][0]
        self.db = self.app.extensions['mongoengine']
        if not self.connection.host is 'localhost':
            assert 0, "Must run tests on localhost!"

    def bulk_insert(self):
        self.User.generate_fake(known_users)
        self.Sensor.generate_fake(known_sensors)
        self.Pod.generate_fake(known_pods)
        self.Notebook.generate_fake(known_notebooks)
        self.Data.generate_fake(known_data)
        self.Message.generate_fake(known_messages)
