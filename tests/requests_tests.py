from . import TestBase
from pea import *
from request_steps import *


def setup_world(app):
    world.data = {}
    world.user = None
    world.password = None
    world.headers = {}
    world.method = None


class RootTests(TestBase):

    def setUp(self):
        super(RootTests, self).setUp()
        setup_world(self.app)
        self.client = self.test_client

    def tearDown(self):
        super(RootTests, self).tearDown()

    def test_making_a_GET_request_to_the_api_at_rootdir(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/')
        And.my_request_method_is('GET')
        And.my_request_data_is(None)
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain(None)
        When.I_make_my_request()
        Then.my_response_status_code_is(200)

    def test_making_a_GET_request_to_api_info_with_bad_key(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/hirefire/' +
                                                      'catbreath' + '/info')
        And.my_request_method_is('GET')
        And.my_request_data_is(None)
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain({'Content-type': 'application/json'})
        When.I_make_my_request()
        Then.my_response_status_code_is(404)

    def test_making_a_POST_request_to_the_api_at_rootdir(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/')
        And.my_request_method_is('POST')
        And.my_request_data_is(None)
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain(None)
        When.I_make_my_request()
        Then.my_response_status_code_is(405)
