"""
Dummy Task example.
"""

import task_manager
import time


class DummyTask(task_manager.Task):

    def __init__(self, n=10, **kwargs):
        super(DummyTask, self).__init__(self, **kwargs)
        self.n = n

    def call(self):
        self.logger.debug("DummyTask.call")
        for i in range(self.n):
            self.logger.debug(i)
            self.data = i
            self.message = "message %s" % i
            self.progress = 100.0 * i/self.n
            time.sleep(1)
        self.status = "resolved"
        self.progress = 100.0
