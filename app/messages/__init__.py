import requests
from requests.auth import HTTPBasicAuth
import time
import json
import struct
from random import choice, randint
from ..names import firstnames, lastnames
from ..HMACAuth import compute_signature
from ..utils import InvalidMessageException
from flask import current_app


class Message(object):

    def __init__(self, data=None, db=None):
        self.db = db if db else None
        self.pod_serial_number_length = 4
        self.type = 'unknown'
        self.frame = self.__class__.__name__
        self.format = [
            {'name': 'frame_id', 'length': 2},
            {'name': 'pod_id', 'length': self.pod_serial_number_length}
        ]
        self.SID_LENGTH = 2
        self.NOBS_LENGTH = 2
        self.TIME_LENGTH = 8
        if data:
            # Stuff that every message should have:
            self.etags = {}
            self.message = data
            self._id = data['_id'] if '_id' in data else None
            self.source = data['source'] if 'source' in data else None
            self.status = data['status'] if 'status' in data else None
            self.content = str(data['message']) if 'message' in data else None
            self.number = data['number'] if 'number' in data else None
            self.pod_name = data['p'] if 'p' in data else None
            self.href = data['_links']['self']['href']
            self._created = data['_created'] if '_created' in data \
                else self.get_now()
            self.url = 'https://' + self.href
            self.json = data
            self.pod_data = None
        else:
            assert 0, "Must provide message data to initialize SMS"

        # New things we will need to determine:
        if self.status == 'posted' and self.type == 'data':
            self.nobs = data['nobs']
            self.nposted = data['nposted']
            self.data_ids = data['data_ids']
        else:
            self.nobs = 0
            self.nposted = 0
            self.data_ids = []
            self.data = None

    def get_length(self, value):
        seq = self.format
        return (item for item in seq if item["name"] == value).next()['length']

    def get_position(self, value):
        seq = self.format
        attr = 'name'
        loc = next(index for (index, d) in enumerate(seq) if d[attr] == value)
        start = 0
        for i in range(0, loc):
            start += self.format[i]['length']
        length = self.get_length(value)
        end = start + length
        return (start, end)

    def format_length(self):
        length = 0
        for item in self.format:
            length += item['length']
        return length

    def post(self):
        if not self.status == 'invalid':
            print "posting data"
            nposted = 0
            url = current_app.config['API_URL'] + '/data'
            headers = {'content-type': 'application/json'}
            data = json.dumps(self.data)
            token = current_app.config['API_AUTH_TOKEN']
            auth = HTTPBasicAuth(
                'api',
                compute_signature(token, url, data))
            d = requests.post(url=url, data=data, headers=headers, auth=auth)
            if d.status_code == 201:
                items = d.json()
                if self.nobs > 1:
                    for item in items:
                        print 'Item status: ' + \
                            str(item[current_app.config['STATUS']])
                        if not item[current_app.config['STATUS']] == \
                                current_app.config['STATUS_ERR']:
                            nposted = nposted + 1
                            self.data_ids.append(item[u'_id'])
                else:
                    print 'Item status: ' + \
                        str(items[current_app.config['STATUS']])
                    if not items[current_app.config['STATUS']] == \
                            current_app.config['STATUS_ERR']:
                        nposted = nposted + 1
                        self.data_ids.append(items[u'_id'])
            else:
                print json.dumps(d.json())
            self.nposted = nposted
        else:
            pass

    def patch(self):
        patched = {}
        # FIRST PATCH THE MESSAGE CONTENT:
        patched['type'] = self.type
        patched['frame'] = self.frame
        patched['status'] = self.status
        # IF WE PARSED SUCCESFULLY....
        if self.status is 'parsed':
            patched['pod'] = str(self.pod()['_id'])
            patched['pod_name'] = self.pod()['name']
            patched['status'] = 'posted'
        else:  # OR NOT
            patched['pod'] = None
            patched['pod_name'] = None
        # IF THIS IS A DATA MESSAGE.....
        if self.type is 'data':
            patched['nobs'] = self.nobs
            if self.nposted > 0:
                patched['status'] = 'posted'
                patched['nposted'] = self.nposted
                patched['data'] = self.data_ids
                patched['notebook'] = self.pod()['_notebook']
                status = {}
                v = next((item for item in self.data
                         if item["sensor"] == "53a06d3f0299cf3e11caa88d"),
                         None)
                # But we need to extract the vbatt_tellit out of the data.
                # Use the Sensor Id. HACKY!
                if v:
                    status['last'] = v['t']
                    status['voltage'] = v['v']
                    status['mode'] = 'normal'
                if self.number and not self.number == self.pod()['number']:
                    status['number'] = self.number
                if status:
                    url = self.stat_url()
                    data = json.dumps(status)
                    token = current_app.config['API_AUTH_TOKEN']
                    # Don't forget to set the content type to json
                    headers = {'If-Match': str(self.stat_etag()),
                               'content-type': 'application/json'}
                    auth = HTTPBasicAuth(
                        'api',
                        compute_signature(token, url, data))
                    requests.patch(
                        url=url,
                        data=data,
                        headers=headers,
                        auth=auth)
                    # Need to have some graceful failures here...
        # PATCH THE MESSAGE...
        try:
            # SHOULD THIS BE DONE WITH PYMONGO?
            data = json.dumps(patched)
            url = self.url
            headers = {'If-Match': str(self.msg_etag()),
                       'content-type': 'application/json'}
            token = current_app.config['API_AUTH_TOKEN']
            auth = HTTPBasicAuth(
                'api',
                compute_signature(token, url, data))
            p = requests.patch(url=url, data=data, headers=headers, auth=auth)
            response = {}
            if p.status_code == requests.codes.ok:
                response['status'] = patched['status']     # RQ reporting
                response['patch code'] = p.status_code     # RQ reporting
                if p.json()[current_app.config['STATUS']] == \
                        current_app.config['STATUS_ERR']:
                    print 'PATCH:[' + str(response['patch code']) + ']:' + \
                        p.json()[current_app.config['STATUS']] + ':' + \
                        json.dumps(p.json()[current_app.config['ISSUES']])
                else:
                    print 'PATCH:[' + str(response['patch code']) + \
                        ']:' + p.json()[current_app.config['STATUS']] + ':' + \
                        str(self.url) + ':status:' + patched['status']
            else:
                print 'PATCH: [' + str(p.status_code) + ']:' + 'request failed'
            return response
        except:
            assert 'Error sending patch request to server'

    def parse(self):
        """
        go through the user data of the message
        | sid | nObs | unixtime1 | value1 | unixtime2 | value2 | ... | valueN |
        sid = 1byte
        nObs = 1byte
        unixtime = 4 bytes LITTLE ENDIAN
        value = look up length
        """
        i = self.get_length('frame_id') + self.get_length('pod_id')
        self.status = 'parsed'
        self.data = []
        self.nobs = 0  # Initialize observation counter
        while i < len(self.content):
            try:
                sid = self.get_sid(i)
            except:
                print 'error reading sid'
                self.status = 'invalid'
                return
            try:
                sensor = self.get_sensor(sid)
            except:
                print 'error reading sensor from database'
                self.status = 'invalid'
                return
            i += 2
            try:
                nobs = self.get_nobs(i)
            except:
                self.status = 'invalid'
                print 'error reading nobs'
                return
            i += 2
            self.nobs += nobs
            try:
                if sensor['context'] == '':
                    sensor_string = str(sensor['variable'])
                else:
                    sensor_string = str(sensor['context']) + ' ' + \
                        str(sensor['variable'])
            except:
                self.status = 'invalid'
                print 'error reading sensor string'
                return

            # add entry for each observation (nObs) by the same sensor
            entry = {}
            while nobs > 0:
                try:
                    entry = {
                        's': sensor_string,
                        'p': str(self.pod()['name']),
                        'sensor': str(sensor['_id']),
                        'pod': {
                            '_id': str(self.pod()['_id']),
                            '_notebook': self.pod()['_notebook']
                            },
                        'loc': {
                            'type': 'Point',
                            'coordinates': [self.lng(), self.lat()]
                        },
                    }
                except:
                    self.status = 'invalid'
                    print 'error creating entry'
                    return
                try:
                    entry['t'] = self.get_time(i)  # Get timestamp
                except:
                    self.status = 'invalid'
                    print 'error reading timestamp'
                    return
                i += 8
                try:
                    entry['v'] = self.get_value(i, sensor)
                except:
                    print 'error reading value'
                    self.status = 'invalid'
                    return

                i += 2*sensor['nbytes']

                # add to big ole json thing
                self.data.append(entry)
                nobs -= 1

    def get_sensor(self, sid):
        return self.db['sensors'].find_one({'sid': sid})

    def get_sid(self, i):
        return int(self.content[i:i+self.SID_LENGTH], 16)

    def get_nobs(self, i):
        return int(self.content[i:i+self.NOBS_LENGTH], 16)

    # Pod and Notebook Identity Functions:
    def pod(self):  # Get the pod document for this message
        if not self.pod_data:  # and self.etags['pod'] == self.pod_etag():
            self.pod_data = self.db['pods'].find_one({'pod_id': self.pod_id()})
        return self.pod_data

    def notebook(self):
        return self.db['pods_notebooks'].find_one(
            {'_id_pod': self.pod()['_id'],
             '_notebook': self.pod()['_notebook']})

    def stat_url(self):
        return str(current_app.config['API_URL'] + '/pods/status/' +
                   str(self.pod()['name']))

    def pod_url(self):
        return current_app.config['API_URL'] + '/pods/' + \
            str(self.pod()['_id'])

    # Pod and Notebook Ids:
    def pod_id(self):
        (start, end) = self.get_position('pod_id')
        try:
            pod_id = int(self.content[start:end], 16)
        except ValueError:
            self.status = 'invalid'
            assert 0, "Invalid Message: " + self.content
        return pod_id

    def msg_etag(self):  # Return this message's etag
        return str(requests.head(self.url).headers['Etag'])

    def stat_etag(self):
        return str(requests.head(self.stat_url()).headers['Etag'])

    def pod_etag(self):
        return str(requests.head(self.pod_url()).headers['Etag'])

    def lat(self):
        return self.notebook()['location']['lat']

    def lng(self):
        return self.notebook()['location']['lng']

    def make_pod_id(self):
        pass
#        pods = app.extensions['pymongo']['MONGO'][1]['pods']
#        return (pods.find().sort('pod_id', -1)[0]['pod_id'] + 1)

    def get_now(self):
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

    def pod_name(self):
        return choice(firstnames) + '-' + choice(lastnames) + \
            '-' + str(randint(1000, 9999))

    def get_time(self, i):
        # parse unixtime to long int, then convert to database time
        try:
            unixtime = struct.unpack(
                '<L',
                self.content[i:i+self.TIME_LENGTH].decode('hex'))[0]
        except:
            raise InvalidMessageException(
                'Error decoding timestamp',
                status_code=400)
        t = time.gmtime(unixtime)
        # dbtime is (e.g.) "Tue, 17 Sep 2013 01:33:56 GMT"
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT", t)

    def get_value(self, i, sensor):
        # parse value based on format string
        try:
            value = struct.unpack(
                str(sensor['byteorder'] + sensor['fmt']),
                self.content[i:i+(2*int(sensor['nbytes']))].decode('hex'))[0]
        except:
            raise InvalidMessageException(
                'Error parsing format string',
                status_code=400)

        # Right here we would do some initial QA/QC based on whatever
        # QA/QC limits we eventually add to the sensor specifications.
        # Not returning the flag yet.
        self.qa_qc(sensor, value)
        return float(value)

    def qa_qc(self, sensor, value):
        pass