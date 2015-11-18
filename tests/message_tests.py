from . import TestBase
from pea import *
from message_steps import *
from app.shared.models.message import NewMessageObject


class TestMessages(TestBase):

    def setUp(self):
        super(TestMessages, self).setUp()
        world.Message = self.Message
        world.Message.drop_collection()

    def tearDown(self):
        super(TestMessages, self).tearDown()
        world.Message.drop_collection()

    def test_generate_one_fake_status_message(self):
        When.I_generate_a_fake_message_with(count=1, frame_id=1)
        And.I_init_my_message_object()
        Then.my_message_object_type_returns('status')
        And.my_Message_objects_has_length(1)
        And.my_message_object_frame_id_returns(1)
        And.my_messageMessage_frame_is('StatusMessage')
        And.my_MessageObject_format_length_is(6)
        And.my_MessageObject_header_length_is(6)
        And.my_MessageObject_format_items_are_only(['frame_id', 'pod_id'])
        And.my_MessageObject_raises_StopIterations_when_value_not_in_format()
        And.my_MessageObject_get_now_returns_format(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

    def test_generate_one_fake_data_message(self):
        When.I_generate_a_fake_message_with(count=1, frame_id=2)
        And.I_init_my_message_object()
        Then.my_message_object_type_returns('data')
        And.my_Message_objects_has_length(1)
        And.my_message_object_frame_id_returns(2)
        And.my_messageMessage_frame_is('DataMessage')
        And.my_MessageObject_format_length_is(6)
        And.my_MessageObject_header_length_is(6)
        And.my_MessageObject_format_items_are_only(['frame_id', 'pod_id'])
        And.my_MessageObject_raises_StopIterations_when_value_not_in_format()
        And.my_MessageObject_get_now_returns_format(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

    def test_generate_one_fake_deploy_message(self):
        When.I_generate_a_fake_message_with(count=1, frame_id=3)
        And.I_init_my_message_object()
        Then.my_message_object_type_returns('deploy')
        And.my_Message_objects_has_length(1)
        And.my_message_object_frame_id_returns(3)
        And.my_messageMessage_frame_is('DeployMessage')
        And.my_MessageObject_format_length_is(30)
        And.my_MessageObject_header_length_is(6)
        And.my_MessageObject_format_items_are_only(
            ['frame_id', 'pod_id', 'mcc', 'mnc',
             'lac', 'cell_id', 'voltage', 'n_sensors']
        )
        And.my_MessageObject_raises_StopIterations_when_value_not_in_format()
        And.my_MessageObject_get_now_returns_format(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

    def test_generate_a_ton_of_fake_messages(self):
        When.I_generate_a_fake_message_with(count=100)
        Then.my_Message_objects_has_length(100)

    def test_DataMessage_object_functionality(self):
        When.I_generate_a_fake_message_with(count=1, frame_id=2)
        And.my_message_content_is(self.DataMessage['message_content'])
        And.I_init_my_message_object()
        Then.my_MessageObject_status_is('queued')
        And.my_MessageObject_pod_id_returns(3931)

    def test_NewMessageObject_create_function(self):
        self.assertRaises(
            AssertionError,
            lambda: NewMessageObject.create(message_type=None)
        )
        self.assertTrue(
            NewMessageObject.create(message_type='invalid').frame ==
            'InvalidMessage'
        )
        self.assertTrue(
            NewMessageObject.create(message_type='whatever').frame ==
            'UnknownMessage'
        )


class TestDataModel(TestBase):

    def setUp(self):
        super(TestDataModel, self).setUp()
        world.Data = self.Data
        world.Data.drop_collection()

    def tearDown(self):
        super(TestDataModel, self).tearDown()
        world.Data.drop_collection()

    def test_Data_generate_fake_functionality(self):
        self.Sensor.drop_collection()
        self.Notebook.drop_collection()
        self.Data.generate_fake(1)

    def test_Data_get_id(self):
        self.User.generate_fake(1)
        self.Sensor.generate_fake(1)
        self.Pod.generate_fake(1)
        self.Notebook.generate_fake(1)
        data = self.Data.generate_fake(1)[0]
        self.assertTrue(data.get_id() == unicode(data.id))

    def test_Data_retr(self):
        self.User.generate_fake(1)
        self.Sensor.generate_fake(1)
        self.Pod.generate_fake(1)
        self.Notebook.generate_fake(1)
        data = self.Data.generate_fake(1)[0]
        self.assertTrue(data. __repr__() == '<Data %r>' % data.value)


class TestNotebookModel(TestBase):

    def setUp(self):
        super(TestNotebookModel, self).setUp()
        world.Notebook = self.Notebook
        world.Notebook.drop_collection()

    def tearDown(self):
        super(TestNotebookModel, self).tearDown()
        world.Notebook.drop_collection()

    def test_Notebook_generate_fake_functionality(self):
        self.Sensor.drop_collection()
        self.Pod.drop_collection()
        self.Notebook.generate_fake(1)

    def test_Notebook_get_id(self):
        notebook = self.Notebook.generate_fake(1)[0]
        self.assertTrue(notebook.get_id() == unicode(notebook.id))

    def test_Data_retr(self):
        notebook = self.Notebook.generate_fake(1)[0]
        self.assertTrue(notebook. __repr__() ==
                        '<Notebook %r>' % notebook.name)
