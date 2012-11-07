import logging


class Task(object):
    """ A basic task object. """
    status = None
    data = None

    def __init__(self, status=None, data=None, logger=logging.getLogger()):
        self.status = status
        self.data = data
        self.logger = logger

    def update_status(self, status):
        self.status = status

    def update_data(self, data):
        self.data = data

    def call(self):
        pass

    def to_dict(self):
        return {
            'status': self.status,
            'data': self.data
        }
