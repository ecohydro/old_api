from . import Message
import requests
from flask import current_app


class NumberMessage(Message):

    def __init__(self, data=None, db=None):
        super(NumberMessage, self).__init__(data=data, db=db)
        self.type = 'data'
        self.frame = self.__class__.__name__
        self.pod_serial_number_length = 0
        self.format[1]['length'] = self.pod_serial_number_length

    def pod_id(self):
        # USE PYMONGO HERE
        if self.pod_id_value is None:
            podurl = current_app.config['API_URL'] + '/pods/?where={"' + \
                'number' + '":"' + self.number + '"}'
            self.pod_id_value = str(
                requests.get(podurl).json()['_items'][0]['pod_id'])
        return self.pod_id_value

    def post(self):
        if not self.status == 'invalid':
            self.post_data()
