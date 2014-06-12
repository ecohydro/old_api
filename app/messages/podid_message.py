from . import Message


class PodIdMessage(Message):

    def __init__(self, data=None, db=None):
        super(PodIdMessage, self).__init__(data=data, db=db)
        self.type = 'data'
        self.frame = self.__class__.__name__

    def post(self):
        if not self.status == 'invalid':
            self.post_data()
