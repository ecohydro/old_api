from . import db
from flask import current_app
import datetime
from messages.invalid_message import InvalidMessage, UnknownMessage
from messages.status_message import StatusMessage
from messages.data_messages import DataMessage
from messages.deploy_messages import DeployMessage, DeployMessageLong


class NewMessageObject(object):
    @staticmethod
    def create(message_type=None):
        if message_type is None:
            assert 0, "Must provide a message_type"
        if message_type == "data":
            return DataMessage()
        if message_type == "status":
            return StatusMessage()
        if message_type == "deploy":
                return DeployMessage()
        if message_type == "deploy_long":
                return DeployMessageLong()
        if message_type == "invalid":
            return InvalidMessage()
        return UnknownMessage()


class Message(db.Document):

    STATUS = ['queued', 'parsed', 'posted', 'unknown', 'invalid']
    SOURCES = ['smssync', 'twilio', 'nexmo', 'pulsepi', 'unknown']

    FRAMES = {
        1: 'status',
        2: 'data',
        3: 'deploy',
        4: 'deploy_long',
        9999: 'invalid'
    }

    # WARNING! THE API WILL EXPECT POSTS TO INCLUDE DB_FIELDS.
    # DO NOT SEND MONGOENGINE FIELDS. THIS IS A KNOWN ISSUE (BUG)
    message_content = db.StringField(
        max_length=170,
        default=None,
        required=True,
        db_field='message_content',
    )
    status = db.StringField(
        choices=STATUS,
        default='queued'
    )
    message_id = db.StringField(
        max_length=40,
        db_field='message_id',
        required=True,
        unique=False
    )
    number = db.StringField(
        max_length=20,
        default='+18888675309')
    time_stamp = db.DateTimeField(
        default=datetime.datetime.now
    )
    source = db.StringField(
        choices=SOURCES,
        required=True
    )
    message_type = db.StringField(
        choices=FRAMES.values() + list(['unknown']),
        db_field='type',
        default='unknown'
    )
    frame_id = db.IntField(
        choices=FRAMES.keys(),
        db_field='frame_id',
        default=None
    )
    pod = db.ReferenceField('Pod')
    notebook = db.ReferenceField('Notebook')
    owner = db.ReferenceField('User')
    meta = {
        'indexes': [
            'source', 'status', 'message_type', 'pod', 'notebook'],
        'index_background': True,
        'ordering': ['-time_stamp'],
        'collection': 'new_messages',
        'allow_inheritance': True
    }

    @staticmethod
    def send_message(number=None, content=None):
        """ Send a message to the Twilio client for testing purposes.
        Uses twilio authentication and account information
        Returns a twilio message object.

        """
        from twilio.rest import TwilioRestClient
        import phonenumbers
        if number is None:
            assert 0, "Must provide number"
        z = phonenumbers.parse(number, None)
        if not phonenumbers.is_valid_number(z):
            assert 0, "Dodgy number."
        if content is None:
            assert 0, "Message content is empty"
        account = current_app.config['TWILIO_ACCOUNT_SID']
        token = current_app.config['TWILIO_AUTH_TOKEN']
        client = TwilioRestClient(account, token)
        message = client.messages.create(
            to=number,
            from_=current_app.config['TWILIO_NUMBER'],
            body=content)
        return message

    @staticmethod
    def generate_fake(count=1, frame_id=None):
        """ Generate a fake message for use in testing

        count - The number of fake messages to generate. Default is 1.

        frame_id - The message type to generate. Default is None.

        frame_id must be one of the values of FRAMES
        If no frame_id is provided, a random one is choosen.

        Returns a list of messages. Use a = generate_fake()[0]
        to obtain a single message object

        """
        from random import choice, randint
        from faker import Faker
        from .notebook import Notebook
        fake = Faker()
        # fake.seed(3123)
        fake_messages = []
        n_notebooks = Notebook.objects().count()
        for i in range(count):
            try:
                if n_notebooks > 0:
                    notebook = Notebook.objects()[randint(
                        0, n_notebooks - 1)]
                else:
                    notebook = Notebook.generate_fake(1)[0]
            except:
                return 'Error: No Notebook objects defined'
            if frame_id is None:
                frame = choice(Message.FRAMES.keys())
            else:
                frame = frame_id
            obj = NewMessageObject.create(Message.FRAMES[frame])
            message_str = obj.create_fake_message(frame, notebook)
            message = Message(
                message_id=str(fake.random_int(min=100000, max=100000000)),
                number=notebook.pod.number,
                source=choice(Message.SOURCES),
                message_content=message_str,
                pod=notebook.pod,
                notebook=notebook,
                owner=notebook.owner
            )
            # try:
            message.message_type = message.get_type()
            message.frame_id = message.get_frame_id()
            message.save()
            fake_messages.append(message)
        # except:
        #        return "Unable to save message"
        return fake_messages

    def __repr__(self):
        return '<Message %r>' % self.message_content

    def __unicode__(self):
        return self.id

    def slack_slash(self):
        raise NotImplementedError

    def get_frame_id(self):
        """ Return the frame_id of a message, based on message content
        """
        try:
            return int(self.message_content[0:2], 16)
        except ValueError:
            return 9999

    def get_type(self):
        """ Return the message type, based on the frame_id
        """
        try:
            return Message.FRAMES[self.get_frame_id()]
        except KeyError:
            return 'invalid'

    def pod_id(self):
        """ Return the pod_id of this message, taken from message content

        Returns None for invalid message.
        Assumes we are using long pod_ids.
        """
        try:
            return int(self.message_content[2:6], 16)
        except ValueError:
            self.status = 'invalid'
            self.save()
            return None

    def get_id(self):
        """ Returns the database id of the current message

        Only available after a message has been saved to the database.
        """
        return unicode(self.id)

    def get_time(self):
        """ Returns the message time_stamp in JSON-friendly format
        """
        return self.time_stamp.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def compute_signature(self):
        """ Generate an encrypted authentication signature for a message.

        Uses get_data to construct the necessary data dictionary.
        Then use compute_signature from utils.py to generate an
        authentication string. This string would be
        used in the HTTPBasicAuth string to verify the authenticity of a
        message posted to the API. The API_AUTH_TOKEN is used to hash
        message content.

        """
        from app.shared.utils import compute_signature
        import json
        data = self.get_data()
        url = current_app.config['API_URL'] + '/messages/' + self.source
        print url
        return compute_signature(
            current_app.config['API_AUTH_TOKEN'],
            url,
            json.dumps(data))

    def get_data(self):
        """ Returns the message data in an API-conformant dictionary

        This is the basic structure that all messages should present when
        posting to the API
        """
        data = {}
        data['message_content'] = self.message_content
        data['time_stamp'] = self.get_time()
        data['source'] = self.source
        data['number'] = self.number
        data['message_id'] = self.message_id
        return data

    def init(self):
        """ Initialize the message class using the class factory function

        Also assigns type-specific parse, post, and slack functions.

        """
        message_object = NewMessageObject.create(self.get_type())
        message_object.init(self)
        # Setup the parse, post, and alert functions for this class:
        self.parse = message_object.parse
        self.post = message_object.post
        self.slack = message_object.slack
        # Store the MessageObject in the message itself:
        self.Message = message_object


class TwilioMessage(Message):

    def __repr__(self):
        return '<TwilioMessage %r>' % self.message_content


class PulsePiMessage(Message):

    def __repr__(self):
        return '<PulsePiMessage %r>' % self.message_content


class SMSSyncMessage(Message):

    def __repr__(self):
        return '<SMSSyncMessage %r>' % self.message_content
