from pea import *
import time


@step
def my_data_frame_id_is(id):
    world.frame_id = id


@step
def my_number_of_fake_messages_is(count):
    world.count = count


@step
def I_generate_a_fake_message_with(count=1, frame_id=None):
    world.messages = world.Message.generate_fake(
        count=count,
        frame_id=frame_id)
    world.message = world.messages[0]


@step
def my_Message_objects_has_length(length):
    world.assertTrue(world.Message.objects().count() == length)


@step
def my_message_object_type_returns(type):
    world.assertTrue(world.message.get_type() == type)


@step
def I_init_my_message_object():
    world.message.init()


@step
def my_message_object_frame_id_returns(frame_id):
    world.assertTrue(world.message.get_frame_id() == frame_id)


@step
def my_messageMessage_frame_is(frame):
    world.assertTrue(world.message.Message.frame == frame)


@step
def my_message_content_is(message_content):
    world.message.message_content = message_content


@step
def my_MessageObject_status_is(status):
    world.assertTrue(
        world.message.Message.status == status
    )


@step
def my_MessageObject_pod_id_returns(pod_id):
    world.assertTrue(
        world.message.Message.pod_id() == pod_id
    )


@step
def my_MessageObject_status_is_set_to(status):
    world.message.Message.status = status


@step
def my_MessageObject_parse_returns(return_stuff):
    world.assertTrue(
        world.message.parse() == return_stuff
    )


@step
def my_MessageObject_format_length_is(length):
    world.assertTrue(
        world.message.Message.format_length() == length
    )


@step
def my_MessageObject_header_length_is(length):
    world.assertTrue(
        world.message.Message.get_header_length() == length
    )


@step
def my_MessageObject_raises_StopIterations_when_value_not_in_format():
    world.assertRaises(
        StopIteration,
        lambda: world.message.Message.get_length('dog')
    )
    world.assertRaises(
        StopIteration,
        lambda: world.message.Message.get_position('dog')
    )


@step
def my_MessageObject_pod_is_set_to(pod):
    world.message.Message.message.pod = pod


@step
def my_MessageObject_format_items_are_only(items):
    world.assertTrue(world.message.Message.get_items() == items)


@step
def my_MessageObject_get_now_returns_format(time_format):
    try:
        time.strptime(world.message.Message.get_now(), time_format)
        return True
    except ValueError:
        return False
