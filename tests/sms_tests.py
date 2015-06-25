from . import TestBase
from pea import *
from sms_steps import *
from requests import HTTPError
from fixtures import TwilioTestData, GenericTestData
from fixtures import SMSSyncTestData

twilio = TwilioTestData()
test = GenericTestData()
smssync = SMSSyncTestData()


def setup_world(app):
    world.data = {}
    world.message_id = None
    world.resource = None
    world.data = {}
    world.test_id = 'test_id'
    world.test_data = 'asd123qsda'
    world.config = app.config
    world.app = app
    world.client = app.test_client


class SMSTestsInitialize(TestBase):

    def setUp(self):
        super(SMSTestsInitialize, self).setUp()
        setup_world(self.app)
        self.client = self.test_client

    def tearDown(self):
        super(SMSTestsInitialize, self).tearDown()

    def test_initializing_an_empty_sms_object(self):
        Given.my_message_id_is(None)
        And.my_resource_is(None)
        And.my_data_is(None)
        When.I_initialize_an_SMS_object()
        Then.SMS_class_is("<class 'app.gateway.SMS.SMS'>")
        And.SMS_name_is('SMS')

    def test_passing_a_message_id_when_initializing_an_SMS_object(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is(None)
        And.my_data_is(None)
        When.I_initialize_an_SMS_object()
        Then.SMS_class_is("<class 'app.gateway.SMS.SMS'>")
        And.SMS_name_is('SMS')
        And.SMS_message_id_is(test.message_id)

    def test_passing_data_when_initializing_an_SMS_object(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is(None)
        And.my_data_is(test.data)
        When.I_initialize_an_SMS_object()
        Then.SMS_class_is("<class 'app.gateway.SMS.SMS'>")
        And.SMS_name_is('SMS')
        And.SMS_message_id_is(test.message_id)

    def test_calling_SMS_clean_without_data_dict(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is(None)
        And.my_data_is(test.data)
        When.I_initialize_an_SMS_object()
        Then.SMS_clean_raises(AttributeError)

    def test_unimplemented_error_for_SMS_get(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is(None)
        And.my_data_is(test.data)
        When.I_initialize_an_SMS_object()
        Then.SMS_get_raises(NotImplementedError)


class SMSTestsCreate(TestBase):

    def setUp(self):
        super(SMSTestsCreate, self).setUp()
        setup_world(self.app)
        self.client = self.test_client

    def tearDown(self):
        super(SMSTestsCreate, self).tearDown()

    def test_creating_an_empty_SMS_object(self):
        Given.my_message_id_is(None)
        And.my_resource_is(None)
        And.my_data_is(None)
        Then.SMS_create_raises(AssertionError)

    def test_creating_an_SMS_object_with_an_invalid_resource(self):
        Given.my_message_id_is(None)
        And.my_resource_is('not_a_valid_resource')
        And.my_data_is(None)
        Then.SMS_create_raises(AssertionError)

    def test_creating_a_twilio_SMS_object_without_a_message_id(self):
        Given.my_message_id_is(None)
        And.my_resource_is('twilio')
        And.my_data_is(None)
        Then.SMS_create_raises(AssertionError)

    def test_creating_a_nexmo_SMS_object_without_a_message_id(self):
        Given.my_message_id_is(None)
        And.my_resource_is('nexmo')
        And.my_data_is(None)
        Then.SMS_create_raises(AssertionError)

    def test_creating_a_twilio_SMS_object_with_a_message_id(self):
        Given.my_message_id_is(twilio.message_id)
        And.my_resource_is('twilio')
        And.my_data_is(None)
        When.I_create_an_SMS_object()
        Then.SMS_message_id_is(twilio.message_id)
        And.SMS_class_is("<class 'app.gateway.SMS.Twilio'>")
        And.SMS_name_is('Twilio')
        And.SMS_resource_is('twilio')

    def test_creating_an_smssync_SMS_object_with_a_message_id(self):
        Given.my_message_id_is('anything')
        And.my_resource_is('smssync')
        And.my_data_is(None)
        When.I_create_an_SMS_object()
        Then.SMS_message_id_is('anything')
        And.SMS_class_is("<class 'app.gateway.SMS.SMSSync'>")
        And.SMS_name_is('SMSSync')
        And.SMS_resource_is('smssync')


class SMSTestsGet(TestBase):

    def setUp(self):
        super(SMSTestsGet, self).setUp()
        setup_world(self.app)
        self.client = self.test_client

    def tearDown(self):
        super(SMSTestsGet, self).tearDown()

    def test_calling_Twilio_get_without_TWILIO_ACCOUNT_SID(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is('twilio')
        When.I_create_an_SMS_object()
        And.my_config_does_not_contain('TWILIO_ACCOUNT_SID')
        Then.SMS_get_raises(KeyError)

    def test_calling_Twilio_get_with_TWILIO_ACCOUNT_SID_as_None(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is('twilio')
        When.I_create_an_SMS_object()
        And.my_config_has_None_for('TWILIO_ACCOUNT_SID')
        Then.SMS_get_raises(TypeError)

    def test_calling_Twilio_get_without_TWILIO_AUTH_TOKEN(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is('twilio')
        When.I_create_an_SMS_object()
        And.my_config_does_not_contain('TWILIO_AUTH_TOKEN')
        self.app.config = world.config
        Then.SMS_get_raises(KeyError)

    def test_calling_Twilio_get_with_TWILIO_AUTH_TOKEN_as_None(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is('twilio')
        When.I_create_an_SMS_object()
        And.my_config_has_None_for('TWILIO_AUTH_TOKEN')
        self.app.config = world.config
        Then.SMS_get_raises(AssertionError)

    def test_calling_Twilio_get_without_TWILIO_URL(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is('twilio')
        When.I_create_an_SMS_object()
        And.my_config_does_not_contain('TWILIO_URL')
        self.app.config = world.config
        Then.SMS_get_raises(KeyError)

    def test_calling_Twilio_get_with_TWILIO_URL_as_None(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is('twilio')
        When.I_create_an_SMS_object()
        And.my_config_has_None_for('TWILIO_URL')
        self.app.config = world.config
        Then.SMS_get_raises(TypeError)

    def test_calling_Twilio_get_with_bad_auth(self):
        Given.my_message_id_is(test.message_id)
        And.my_resource_is('twilio')
        When.I_create_an_SMS_object()
        And.my_twilio_authentication_is_bad()
        Then.SMS_get_raises(HTTPError)

    def test_calling_SMS_get_with_bad_message_id(self):
        Given.my_message_id_is(twilio._bad_id)
        And.my_resource_is('twilio')
        When.I_create_an_SMS_object()
        Then.SMS_get_raises(HTTPError)

    def test_calling_SMS_get_with_test_message_id(self):
        Given.my_message_id_is(twilio.message_id)
        And.my_resource_is('twilio')
        When.I_create_an_SMS_object()
        And.I_call_SMS_get()
        Then.SMS_data_body_is('02dogbarf')


class SMSTestsPost(TestBase):

    def setUp(self):
        super(SMSTestsPost, self).setUp()
        setup_world(self.app)
        self.client = self.test_client

    def tearDown(self):
        super(SMSTestsPost, self).tearDown()

    def test_calling_SMS_post_with_API_URL_as_None(self):
        Given.my_message_id_is(test.message_id)
        And.my_data_is(None)
        And.my_resource_is(None)
        When.I_initialize_an_SMS_object()
        And.my_config_has_None_for('API_URL')
        Then.SMS_post_raises(TypeError)

    def test_calling_SMS_post_without_API_URL(self):
        Given.my_message_id_is(test.message_id)
        And.my_data_is(None)
        And.my_resource_is(None)
        When.I_initialize_an_SMS_object()
        And.my_config_does_not_contain('API_URL')
        Then.SMS_post_raises(KeyError)

    def test_calling_SMS_post_with_API_AUTH_TOKEN_as_None(self):
        Given.my_message_id_is(test.message_id)
        And.my_data_is(None)
        And.my_resource_is(None)
        When.I_initialize_an_SMS_object()
        And.my_config_has_None_for('API_AUTH_TOKEN')
        Then.SMS_post_raises(TypeError)

    def test_calling_SMS_post_without_API_AUTH_TOKEN(self):
        Given.my_message_id_is(test.message_id)
        And.my_data_is(None)
        And.my_resource_is(None)
        When.I_initialize_an_SMS_object()
        And.my_config_does_not_contain('API_AUTH_TOKEN')
        Then.SMS_post_raises(KeyError)

    def test_calling_SMS_post_without_data(self):
        Given.my_message_id_is(test.message_id)
        And.my_data_is(None)
        And.my_resource_is(None)
        When.I_initialize_an_SMS_object()
        Then.SMS_post_raises(AssertionError)

    def test_calling_SMS_post_without_resource(self):
        Given.my_message_id_is(test.message_id)
        And.my_data_is(test.data)
        And.my_resource_is(None)
        When.I_initialize_an_SMS_object()
        Then.SMS_post_raises(AssertionError)


class SMSTestsClean(TestBase):

    def setUp(self):
        super(SMSTestsClean, self).setUp()
        setup_world(self.app)
        self.client = self.test_client

    def tearDown(self):
        super(SMSTestsClean, self).tearDown()

    def test_calling_SMS_clean_with_twilio_test_message(self):
        Given.my_message_id_is(twilio.message_id)
        And.my_resource_is('twilio')
        When.I_create_an_SMS_object()
        And.I_call_SMS_get()
        And.I_call_SMS_clean()
        Then.SMS_data_message_is('02dogbarf')
        Then.SMS_data_keys_are_only(
            ['status', 'source', 'number',
             'time_stamp', 'message', 'mid'])
