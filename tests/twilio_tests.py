from . import TestBase
from pea import *
from request_steps import *
from sms_steps import *
from fixtures import TwilioTestData

twilio = TwilioTestData()


def setup_world(app):
    world.data = {}
    world.user = None
    world.password = None
    world.headers = {}
    world.hirefire_token = app.config['HIREFIRE_TOKEN']
    world.method = None


class TwilioTests(TestBase):

    def setUp(self):
        super(TwilioTests, self).setUp()
        setup_world(self.app)
        self.client = self.test_client

    def tearDown(self):
        super(TwilioTests, self).tearDown()

    def test_making_a_GET_request_to_the_gateway_at_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('GET')
        And.my_request_data_is(None)
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain(None)
        When.I_make_my_request()
        Then.my_response_status_code_is(405)

    def test_making_a_POST_request_with_JSON_to_the_gateway_at_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('POST')
        And.my_request_data_is({})
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain({'Content-type': 'application/json'})
        When.I_make_my_request()
        Then.my_response_status_code_is(400)
        And.my_response_data_status_is('ERR')
        And.my_response_data_error_message_is('POST requires FORM data')

    def test_making_a_POST_request_with_no_FORM_data_to_gateway_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_method_is('POST')
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_data_is({})
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain(
            {'Content-type': 'application/x-www-form-urlencoded'})
        When.I_make_my_request()
        Then.my_response_status_code_is(400)
        And.my_response_data_status_is('ERR')
        And.my_response_data_error_message_is('No form data provided')

    def test_making_a_POST_request_with_no_Twilio_header_to_gateway(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('POST')
        And.my_request_data_is({'1': 'a', '2': 'b'})
        And.my_request_authenticates_with_user(None)
        And.my_request_authenticates_with_password(None)
        And.my_request_headers_contain(
            {'Content-type': 'application/x-www-form-urlencoded'})
        When.I_make_my_request()
        Then.my_response_status_code_is(401)
        And.my_response_data_status_is('ERR')
        And.my_response_data_error_message_is(
            'Must provide X-Twilio-Signature header')

    def test_making_a_PUT_request_to_the_gateway_at_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('PUT')
        When.I_make_my_request()
        Then.my_response_status_code_is(405)

    def test_making_a_PATCH_request_to_the_gateway_at_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('PATCH')
        When.I_make_my_request()
        Then.my_response_status_code_is(405)

    def test_making_a_POST_with_invalid_Twilo_header_to_gateway_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('POST')
        And.my_request_data_is(twilio.data)
        And.my_X_Twilio_Signature_is(twilio.signature + 'oops')
        When.I_make_my_request()
        Then.my_response_status_code_is(403)

    def test_making_a_POST_with_valid_Twilo_header_to_gateway_at_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('POST')
        And.my_request_data_is(twilio.data)
        And.my_X_Twilio_Signature_is(twilio.signature)
        When.I_make_my_request()
        Then.my_response_status_code_is(202)
        And.my_response_body_is('<Response></Response>')

    def test_making_a_POST_without_TWILIO_POST_URL_to_gateway_at_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('POST')
        And.my_request_data_is(twilio.data)
        And.my_X_Twilio_Signature_is(twilio.signature)
        And.my_config_does_not_contain('TWILIO_POST_URL')
        self.app.config = world.config
        When.I_make_my_request()
        Then.my_response_status_code_is(500)

    def test_making_a_POST_without_TWILIO_AUTH_to_gateway_at_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('POST')
        And.my_request_data_is(twilio.data)
        And.my_X_Twilio_Signature_is(twilio.signature)
        And.my_config_does_not_contain('TWILIO_AUTH_TOKEN')
        self.app.config = world.config
        When.I_make_my_request()
        Then.my_response_status_code_is(500)

    def test_making_a_POST_TWILIO_POST_URL_None_to_gateway_at_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('POST')
        And.my_request_data_is(twilio.data)
        And.my_X_Twilio_Signature_is(twilio.signature)
        And.my_config_has_None_for('TWILIO_POST_URL')
        self.app.config = world.config
        When.I_make_my_request()
        Then.my_response_status_code_is(500)

    def test_making_a_POST_TWILIO_AUTH_None_to_gateway_at_twilio(self):
        Given.I_am_making_a_request_with_a(self.client)
        And.my_request_is_made_to_the_resource_called('/gateway/twilio')
        And.my_request_method_is('POST')
        And.my_request_data_is(twilio.data)
        And.my_X_Twilio_Signature_is(twilio.signature)
        And.my_config_has_None_for('TWILIO_AUTH_TOKEN')
        self.app.config = world.config
        When.I_make_my_request()
        Then.my_response_status_code_is(500)
