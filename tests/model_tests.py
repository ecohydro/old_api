from . import TestBase


class TestModel(TestBase):

    def setUp(self):
        super(TestModel, self).setUp()

    def tearDown(self):
        super(TestModel, self).tearDown()

    def test_data_model(self):
        d = self.Data.objects().first()
        self.assertTrue('time_stamp' in dir(d))
