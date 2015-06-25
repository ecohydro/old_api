from . import TestBase


class TestApp(TestBase):

    def setUp(self):
        super(TestApp, self).setUp()

    def tearDown(self):
        super(TestApp, self).tearDown()

    def test_slacker_connection(self):
        from app import slack
        r = slack.api.test()
        self.assertTrue(r.successful)

    def test_rq_connections(self):
        from app import post_q, gateway_q, mqtt_q
        self.assertTrue(post_q.connection.ping())
        self.assertTrue(gateway_q.connection.ping())
        self.assertTrue(mqtt_q.connection.ping())

    def test_app_settings(self):
        self.assertTrue(
            self.app.settings['DOMAIN']['data']['resource_methods'] ==
            ['GET']
        )
        self.assertTrue(
            self.app.settings['DOMAIN']['sensor']['resource_methods'] ==
            ['GET']
        )
        self.assertTrue(
            self.app.settings['DOMAIN']['user']['resource_methods'] ==
            ['GET', 'POST']
        )
