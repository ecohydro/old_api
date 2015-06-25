from pea import *
from app.gateway.SMS import SMS


@step
def my_message_id_is(message_id):
    world.message_id = message_id


@step
def my_resource_is(resource):
    world.resource = resource


@step
def my_data_is(data):
    world.data = data


@step
def my_config_is(config):
    if not config == 'default':
        world.config = config
    else:
        pass


@step
def my_config_has_None_for(config_var):
    world.config[config_var] = None


@step
def my_config_does_not_contain(config_var):
    world.config.pop(config_var)


@step
def I_initialize_an_SMS_object():
    world.SMS = SMS(
        message_id=world.message_id,
        resource=world.resource,
        data=world.data)


@step
def I_call_SMS_get():
    world.SMS.get()


@step
def I_call_SMS_clean():
    world.SMS.clean()


@step
def I_create_an_SMS_object():
    world.SMS = SMS.create(
        message_id=world.message_id,
        resource=world.resource,
        data=world.data)


@step
def SMS_class_is(expected):
    assert str(expected) == str(world.SMS.__class__)


@step
def SMS_name_is(expected):
    assert str(expected) == str(world.SMS.__class__.__name__)


@step
def SMS_resource_is(expected):
    assert str(expected) == str(world.SMS.resource())


@step
def SMS_message_id_is(expected):
    assert str(expected) == str(world.SMS.message_id)


@step
def SMS_data_is(expected):
    assert str(expected) == str(world.SMS.data)


@step
def SMS_data_message_is(message):
    assert message == world.SMS.data['message_content']


@step
def SMS_init_raises(expected_error):
    world.assertRaises(
        expected_error,
        lambda: SMS(
            message_id=world.message_id,
            resource=world.resource,
            data=world.data))


@step
def SMS_create_raises(error):
    world.assertRaises(
        error,
        lambda: SMS.create(
            message_id=world.message_id,
            resource=world.resource,
            data=world.data))


@step
def SMS_clean_raises(expected_error):
    world.assertRaises(expected_error, lambda: world.SMS.clean())


@step
def SMS_get_raises(expected_error):
    world.assertRaises(expected_error, lambda: world.SMS.get())


@step
def SMS_post_raises(expected_error):
    world.assertRaises(expected_error, lambda: world.SMS.post())


@step
def my_twilio_authentication_is_bad():
    world.config['TWILIO_ACCOUNT_SID'] = 'donkey kong'
    world.config['TWILIO_AUTH_TOKEN'] = 'let me do it'


@step
def SMS_data_body_is(expected):
    world.assertEqual(expected, world.SMS.data['body'])


@step
def SMS_data_keys_are_only(key_list):
    assert len(set(world.SMS.data.keys()).difference(key_list)) == 0
