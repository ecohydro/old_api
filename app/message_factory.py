import requests
from messages.invalid_message import InvalidMessage
from messages.status_message import StatusMessage
from messages.podid_message import PodIdMessage
from messages.number_message import NumberMessage
from messages.deploy_message import DeployMessage
from flask import current_app


class MessageFactory(object):
    @staticmethod
    def create(data=None, url=None, db=None):
        if not db:
            assert 0, "Must provide PyMongo db object"

        if data is None and url is None:
            assert 0, "Must provide a url or message data"
        if url is not None:
            try:
                r = requests.get(str(url))
                if r.status_code == requests.codes.ok:
                    data = r.json()
                else:
                    assert 0, "Bad url (" + str(r.status_code) + \
                              "): " + str(url)
            except Exception as e:
                e.args += ("Connection error", str(url))
                raise

        try:  # Catch invalid messages
            frame_number = int(str(data['message'][0:2]), 16)
        except ValueError:
            frame_number = 99
        try:  # Catch undefined Frame IDs.
            type = current_app.config['FRAMES'][frame_number]
        except KeyError:
            type = current_app.config['FRAMES'][99]
        if type == "number":
            return NumberMessage(data, db)
        if type == "pod_id":
            return PodIdMessage(data, db)
        if type == "status":
            return StatusMessage(data, db)
        if type == "invalid":
            return InvalidMessage(data, db)
        if type == "deploy":
            return DeployMessage(data, db)
        assert 0, "Bad SMS creation: " + type
