from . import TestBase
import json
from pea import *
from request_steps import *


def setup_world(app):
    world.data = {}
    world.user = None
    world.password = None
    world.headers = {}
    world.hirefire_token = app.config['HIREFIRE_TOKEN']
    world.method = None


class SMSSyncTests(TestBase):

    def setUp(self):
        super(SMSSyncTests, self).setUp()
        setup_world(self.app)
        self.client = self.test_client

    def tearDown(self):
        super(SMSSyncTests, self).tearDown()

    def test_making_a_GET_request_to_the_gateway_at_smssync(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/smssync')
        And.my_request_method_is('GET')
        And.my_request_data_is(None)
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain(None)
        When.I_make_my_request()
        Then.my_response_status_code_is(405)


# SMSSync POST Request Tests
    def test_making_a_POST_request_w_FORM_data_to_gateway_at_smssync(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/smssync')
        And.my_request_method_is('POST')
        And.my_request_data_is({'1': 'a', '2': 'b'})
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain(
            {'Content-type': 'application/json'})
        When.I_make_my_request()
        Then.my_response_status_code_is(400)
        And.my_response_data_status_is('ERR')
        And.my_response_data_error_message_is('POST requires FORM data')

    def test_making_a_POST_request_with_empty_FORM_to_gateway_at_smssync(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/smssync')
        And.my_request_method_is('POST')
        And.my_request_data_is({})
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain(
            {'Content-type': 'application/x-www-form-urlencoded'}
        )
        When.I_make_my_request()
        Then.my_response_status_code_is(400)
        And.my_response_data_status_is('ERR')
        And.my_response_data_error_message_is('No message data provided')

    def test_making_a_POST_request_with_FORM_no_secret_to_smssync(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/smssync')
        And.my_request_method_is('POST')
        And.my_request_data_is({'message': 'a', '2': 'b'})
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain(
            {'Content-type': 'application/x-www-form-urlencoded'}
        )
        When.I_make_my_request()
        Then.my_response_status_code_is(401)
        And.my_response_data_status_is('ERR')
        And.my_response_data_error_message_is(
            'Message requires authentication: [secret]')

    def test_making_a_POST_request_FORM_and_invalid_secret_to_smssync(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/smssync')
        And.my_request_method_is('POST')
        And.my_request_data_is(
            {'message': 'a', '2': 'b', 'secret': 'this_is_not_the_secret'})
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain(
            {'Content-type': 'application/x-www-form-urlencoded'}
        )
        When.I_make_my_request()
        Then.my_response_status_code_is(403)
        And.my_response_data_status_is('ERR')
        And.my_response_data_error_message_is(
            'Message failed authentication: [secret] is incorrect')

    def test_making_a_PUT_request_to_the_gateway_at_smssync(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/smssync')
        And.my_request_method_is('PUT')
        When.I_make_my_request()
        Then.my_response_status_code_is(405)

    def test_making_a_PATCH_request_to_the_gateway_at_smssync(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/smssync')
        And.my_request_method_is('PATCH')
        When.I_make_my_request()
        Then.my_response_status_code_is(405)
