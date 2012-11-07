from .task import Task
from blinker import Signal


class SignalingTask(Task):
    """ A Task which sends signals when its attributes are updated. """
    on_status_update = Signal()
    on_data_update = Signal()
    on_update = Signal()

    def __init__(self, *args, **kwargs):
        Task.__init__(self, *args, **kwargs)

    def update_status(self, status, silent=False):
        Task.update_status(self, status)
        if not silent:
            self.on_status_update.send(self)
            self.on_update.send(self)

    def update_data(self, data, silent=False):
        Task.update_data(self, data)
        if not silent:
            self.on_data_update.send(self)
            self.on_update.send(self)
