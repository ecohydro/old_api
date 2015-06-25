from . import TestBase


class TestHMACAuth(TestBase):

    def setUp(self):
        super(TestHMACAuth, self).setUp()

    def tearDown(self):
        super(TestHMACAuth, self).tearDown()

    def test_init(self):
        from app.HMACAuth import HMACAuth
        import os
        hmac = HMACAuth()
        self.assertTrue(hmac.token == os.getenv('API_AUTH_TOKEN'))
        hmac = HMACAuth(token='test')
        self.assertTrue(hmac.token == 'test')

    def test_check_auth(self):
        from app.HMACAuth import HMACAuth
        hmac = HMACAuth()
        userid = None
        uri = None
        data = None
        hmac_hash = None
        resource = None
        method = 'HEAD'
        self.assertTrue(hmac.check_auth(
            userid, uri, data, hmac_hash, resource, method))
        method = 'OPTIONS'
        self.assertTrue(hmac.check_auth(
            userid, uri, data, hmac_hash, resource, method))
