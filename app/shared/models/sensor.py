from . import db
from datetime import datetime


class Sensor(db.Document):

    # TODO: Add format and byteorder choices...
    BYTEORDERS = ['@', '=', '<', '>', '!']
    FORMATS = {
        'x': 0, 'c': 1, 'b': 1, 'B': 1, '?': 1, 'h': 2, 'H': 2,
        'i': 4, 'I': 4, 'l': 4, 'L': 4, 'q': 8, 'Q': 8, 'f': 4,
        'd': 8}

    name = db.StringField()
    created = db.DateTimeField(default=datetime.now())
    updated = db.DateTimeField(default=datetime.now())
    sid = db.IntField(unique=True)
    context = db.StringField()
    context_short = db.StringField()
    variable = db.StringField()
    variable_short = db.StringField()
    nbytes = db.IntField(
        choices=list(set(FORMATS.values())),
        default=FORMATS['f']
    )
    fmt = db.StringField(
        choices=FORMATS.keys(),
        default='f')
    byteorder = db.StringField(
        default='<')
    info = db.StringField()
    unit = db.StringField()
    m = db.FloatField(
        default=1
    )
    b = db.FloatField(
        default=0
    )
    sensing_chip = db.StringField(
        default=None
    )
    observations = db.IntField(
        default=0
    )
    # updated = db.DateTimeField()
    # created = db.DateTimeField()
    meta = {
        'collection': 'sensors'
    }

    def __repr__(self):
        return '<Sensor %r>' % self.name

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def generate_fake(count=100):
        from random import randint
        from faker import Faker
        fake = Faker()
        fake_sensors = []
        i = 0
        while i < count:
            sensor = Sensor(
                name=fake.domain_word(),
                sid=randint(1, 1024),
                context=fake.word(),
                variable=fake.word(),
                info=fake.catch_phrase(),
                unit='b/s',
            )
            try:
                sensor.save()
                fake_sensors.append(sensor)
                i += 1
            except:
                pass
        return fake_sensors
