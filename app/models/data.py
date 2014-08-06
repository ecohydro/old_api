from .. import db
import datetime


class Data(db.Document):

    time_stamp = db.DateTimeField(
        db_field='t',
        default=datetime.datetime.now())
    value = db.FloatField(
        db_field='v',
        default=None)
    location = db.PointField(db_field='loc')
    # Pod and Sensor names will not change:
    # Define links to Pod, Notebook, and Sensor collections:
    # Note: The API will need to return only
    # notebook_id, pod_name, and sensor_name instead of references...
    notebook = db.ReferenceField('Notebook', db_field='nbk')
    pod = db.ReferenceField('Pod', db_field='pod')
    sensor = db.ReferenceField('Sensor', db_field='s')
    variable = db.StringField()
    pod_name = db.StringField(db_field='p')

    meta = {
        'collection': 'data',
        'ordering': ['-time_stamp'],
        'index_background': True,
        'indexes': [
            'notebook',
            ('notebook', 'sensor'),
            'location',
            ('location', '-time_stamp'),
            'pod',
            'sensor',
        ]
    }

    def __repr__(self):
        return '<Data %r>' % self.value

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def generate_fake(count=1000):
        from faker import Faker
        from random import random, randint, sample
        from .notebook import Notebook
        from .sensor import Sensor

        fake = Faker()
        fake.seed(3123)
        fake_data = []
        for i in range(count):
            try:
                if Sensor.objects().count() > 0:
                    sensor = Sensor.objects()[
                        randint(0, Sensor.objects().count()-1)
                    ]
                else:
                    sensor = Sensor.generate_fake(1)[0]
            except:
                return "Error: No Sensor objects defined"
            try:
                if Notebook.objects().count() > 0:
                    notebook = Notebook.objects()[
                        randint(0, Notebook.objects().count()-1)
                    ]
                else:
                    notebook = Notebook.generate_fake(1)[0]
            except:
                return "Error: No Notebook objects defined."
            data = Data(
                time_stamp=fake.date_time_this_month(),
                location=notebook.location,
                # Sensor and pod names are fixed.
                variable=str(sensor.context) + ' ' + str(sensor.variable),
                value=random()*100,
                pod=notebook.pod,
                sensor=sensor,
                notebook=notebook
            )
            try:
                data.save()
                fake_data.append(data)
            except:
                "Data save failed"
        return fake_data
