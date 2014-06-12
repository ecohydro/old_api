from . import Message


class StatusMessage(Message):

    def __init__(self, data=None, db=None):
        super(StatusMessage, self).__init__(data=data, db=db)
        self.type = 'status'
        self.frame = self.__class__.__name__

    def parse(self):
        i = 2+self.pod_serial_number_length
        ##################################################################
        # |   LAC  |   CI   | nSensors |  sID1  |  sID1  | ... |  sIDn  |
        # | 2 byte | 8 byte |  1 byte  | 1 byte | 1 byte | ... | 1 byte |
        ##################################################################
        # make sure message is long enough to read everything

        lac = int(self.content[i:i+4], 16)
        i += 4
        cell_id = int(self.content[i:i+4], 16)
        i += 4
        n_sensors = int(self.content[i:i+2], 16)
        i += 2
        # now make sure length is actually correct

        # sIDs is list of integer sIDs
        sids = []

        for j in range(n_sensors):
            sids.append(int(self.content[i:i+2], 16))
            i += 2

        self.data = {
            'lac': lac,
            'ci': cell_id,
            'nSensors': n_sensors,
            'sensorlist': sids}

    def post(self):
        pass
