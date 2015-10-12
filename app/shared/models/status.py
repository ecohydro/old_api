from . import db
import datetime

'''

 Generic  status object for a status collection on the API.
 This object allows API workers to generate daily
 status reports on any object within the API

'''

STATUS_TYPES = ['notebook', 'user', 'pod', 'sensor']


class NewStatusObject(object):
    @staticmethod
    def create(status_type=None):
        if status_type is None:
            assert 0, "Must provide a status_type"
        if status_type == "notebook":
            return NotebookStatus()
        if status_type == "user":
            return UserStatus()
        if status_type == "pod":
                return PodStatus()
        if status_type == "sensor":
                return SensorStatus()


class Status(db.Document):

    date = db.DateTimeField(
        db_field='date',
        default=datetime.datetime.today())
    created = db.DateTimeField(default=datetime.datetime.now())
    updated = db.DateTimeField(default=datetime.datetime.now())
    status_type = db.StringField(
        choices=STATUS_TYPES,
        required=True,
    )
    actual_observations = db.IntField(
        default=0
    )
    expected_observations = db.IntField(
        default=0
    )
    # Define links to Pod, Notebook, Sensor, and User collections:
    notebook = db.ReferenceField(
        'Notebook',
        db_field='notebook',
        default=None)
    pod = db.ReferenceField(
        'Pod',
        db_field='pod',
        default=None)
    sensor = db.ReferenceField(
        'Sensor',
        db_field='sensor',
        default=None)
    user = db.ReferenceField(
        'User',
        db_field='user',
        default=None)
    meta = {
        'collection': 'status',
        'ordering': ['-time_stamp'],
        'index_background': True,
        'indexes': [
            'notebook',
            'user',
            'pod',
            'sensor',
        ],
        'allow_inheritance': True,
    }

    def __repr__(self):
        return '<Status %r>' % self.status_type

    def get_id(self):
        return unicode(self.id)

    def display(self):
        return [self.status_type]

    @staticmethod
    def generate_fake(count=10):
        from faker import Faker
        from random import randint, choice
        from .notebook import Notebook
        from .sensor import Sensor
        from .pod import Pod
        from .user import User

        fake = Faker()
        fake_status = []  # Intialize the fake status list
        num_sensors = Sensor.objects().count()
        num_notebooks = Notebook.objects().count()
        num_pods = Pod.objects().count()
        num_users = User.objects().count()
        if num_sensors is 0:
            return "Error: No Sensor objects defined." \
                " Use Sensor.generate_fake()"
        if num_notebooks is 0:
            return "Error: No Notebook objects defined." \
                " Use Notebook.generate_fake()"
        if num_pods is 0:
            return "Error: No Pod objects defined." \
                " Use Pod.generate_fake()"
        if num_users is 0:
            return "Error: No User objects defined." \
                " Use User.generate_fake()"
        for i in range(count):
            # Select a random status type:
            status_type = choice(STATUS_TYPES)
            # First set all the status objects to None:
            sensor = None
            notebook = None
            user = None
            pod = None
            # Assign a random object depending on status_type:
            if status_type is 'sensor':
                try:
                    sensor = Sensor.objects()[
                        randint(0, num_sensors - 1)
                    ]
                except:
                    return "Error: No Sensor objects defined"
            if status_type is 'notebook':
                try:
                    notebook = Notebook.objects()[
                        randint(0, num_notebooks - 1)
                    ]
                except:
                    return "Error: No Notebook objects defined."
            if status_type is 'user':
                try:
                    user = User.objects()[
                        randint(0, num_users - 1)
                    ]
                except:
                    return "Error: No User objects defined."
            if status_type is 'pod':
                try:
                    pod = Pod.objects()[
                        randint(0, num_pods - 1)
                    ]
                except:
                    return "Error: No User objects defined."
            # Define the actual and expected observations:
            actual_observations = randint(0, 100)
            expected_observations = actual_observations - \
                randint(0, actual_observations)
            status = Status(
                status_type=status_type,
                date=fake.date_time_this_month(),
                # Sensor and pod names are fixed.
                actual_observations=actual_observations,
                expected_observations=expected_observations,
                pod=pod,
                sensor=sensor,
                notebook=notebook,
                user=user,
            )
            try:
                status.save()
            except:
                return "Error: Data save failed"
            fake_status.append(status)
        return fake_status


class NotebookStatus(Status):

    def __repr__(self):
        return '<NotebookStatus %r>' % self.notebook.name


class PodStatus(Status):

    def __repr__(self):
        return '<PodStatus %r>' % self.notebook.name


class UserStatus(Status):

    def __repr__(self):
        return '<UserStatus %r>' % self.user.id


class SensorStatus(Status):

    def __repr__(self):
        return '<SensorStatus %r>' % self.sensor.name
