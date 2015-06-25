from pea import *
import base64
import json


# Request Steps:
@step
def I_am_making_a_request_with_a(client):
    world.client = client


@step
def my_request_is_made_to_the_resource_called(resource):
    world.resource = resource


@step
def my_query_string_is(query_string):
    world.query_string = query_string


@step
def my_request_method_is(method):
    world.method = method


@step
def my_request_data_is(data):
    world.data = data


@step
def my_request_authenticates_with_user(user):
    world.user = user


@step
def my_request_authenticates_with_password(password):
    world.password = password


@step
def my_request_headers_contain(headers):
    if headers:
        world.headers = headers
    if world.user and world.password:
        world.headers['Authentication'] = 'Basic ' + \
            base64.b64encode(world.user + ':' + world.password)


# Action Steps:
@step
def I_make_my_request():
    world.response = world.client.open(
        world.resource,
        method=world.method,
        data=world.data,
        headers=world.headers)


@step
def I_make_my_get_request():
    world.response = world.client.open(
        world.resource,
        method=world.method,
        )


# Response Steps:
@step
def my_response_status_code_is(expected):
    print int(world.response.status_code)
    assert int(expected) == int(world.response.status_code)


@step
def my_response_data_error_message_is(expected):
    assert str(expected) == \
        str(json.loads(world.response.get_data())['error'])


@step
def my_response_data_status_is(expected):
    assert str(expected) == \
        str(json.loads(world.response.get_data())['status'])


@step
def my_response_data_status_code_is(expected):
    assert int(expected) == \
        int(json.loads(world.response.get_data())['status_code'])


@step
def my_twilio_response_link_is(expected):
    world.link = expected


@step
def my_response_body_is(expected):
    assert str(expected) == str(world.response.get_data())


@step
def my_X_Twilio_Signature_is(signature):
    world.headers['X-Twilio-Signature'] = signature
