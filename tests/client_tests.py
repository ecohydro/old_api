from . import TestBase
import base64
import json
from mongoengine import Q


class TestClient(TestBase):

    def setUp(self):
        super(TestClient, self).setUp()

    def tearDown(self):
        super(TestClient, self).tearDown()

    def test_get_users_as_admin(self):
        self.User.create_administrator()
        user = self.User.objects(role='admin').first()
        self.assertTrue(user.role == 'admin')
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(user.api_key + ':')
        }
        url = 'users'
        method = 'GET'
        client = self.test_client
        resp = client.open(url, method=method, headers=headers)
        self.assertTrue(resp.status_code == 200)
        meta = json.loads(resp.data)['_meta']
        self.assertTrue(meta['total'] == self.User.objects().count())

    def test_get_admin_only_resources_as_user(self):
        user = self.User.generate_fake(count=1)[0]
        self.assertTrue(user.role == 'user')
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(user.api_key + ':')
        }
        # user can't get a different user's information
        method = 'GET'
        url = 'messages/twilio'
        client = self.test_client
        resp = client.open(url, method=method, headers=headers)
        self.assertTrue(resp.status_code == 401)

    def test_get_user_pods(self):
        user = self.User.generate_fake(count=3)[0]
        self.Pod.generate_fake(count=50)
        pod = self.Pod.objects().first()
        pod.owner = user
        pod.save()
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(user.api_key + ':')
        }
        url = 'pods'
        method = 'GET'
        client = self.test_client
        resp = client.open(url, method=method, headers=headers)
        self.assertTrue(resp.status_code == 200)
        print json.loads(resp.data)
        meta = json.loads(resp.data)['_meta']
        self.assertTrue(meta['total'] == self.Pod.objects(owner=user).count())

    def test_get_user_data(self):
        user = self.User.generate_fake(count=3)[0]
        self.Sensor.generate_fake(count=4)
        self.Notebook.generate_fake(count=10)
        self.Data.generate_fake(count=100)
        owned_or_public = self.Data.objects(
            Q(owner=user) | Q(public=True)
        ).count()
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(user.api_key + ':')
        }
        url = 'data'
        method = 'GET'
        client = self.test_client
        resp = client.open(url, method=method, headers=headers)
        meta = json.loads(resp.data)['_meta']
        self.assertTrue(meta['total'] == owned_or_public)

    def test_get_user_notebook(self):
        user = self.User.generate_fake(count=3)[0]
        self.Sensor.generate_fake(count=4)
        self.Notebook.generate_fake(count=10)
        owned_or_public = self.Notebook.objects(
            Q(owner=user) | Q(public=True)
        ).count()
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(user.api_key + ':')
        }
        url = 'notebooks'
        method = 'GET'
        client = self.test_client
        resp = client.open(url, method=method, headers=headers)
        meta = json.loads(resp.data)['_meta']
        self.assertTrue(meta['total'] == owned_or_public)
