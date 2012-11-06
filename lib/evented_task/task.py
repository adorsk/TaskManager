from blinker import signal

class Task(object):
    status = None
    data = None
    on_status_update = Signal()
    on_data_update = Signal()
    on_update = Signal()

    def __init__(self, status=None, data=None):
        self.status = status
        self.data = data


    def update_status(self, status, silent=False):
        self.status = status
        if not silent:
            self.on_status_update.send(self)
            self.on_update.send(self)

    def update_data(self, data, silent=False):
        self.data = data
        if not silent:
            self.on_data_update.send(self)
            self.on_update.send(self)

    def call(self):
        pass
