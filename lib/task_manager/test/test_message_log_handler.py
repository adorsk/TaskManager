import unittest
import task_manager
import logging


class MessageLogHandlerTestCase(unittest.TestCase):

    def test_message_log_handler(self):

        class LoggingTask(task_manager.Task):
            def __init__(self, **kwargs):
                super(LoggingTask, self).__init__(self, **kwargs)
                self.message_handler = self.get_message_log_handler()
                self.logger.addHandler(self.message_handler)
                self.logger.setLevel(logging.DEBUG)

        logging_task = LoggingTask()
        logging_task.logger.debug('testo')
        assert logging_task.message == 'testo'

if __name__ == "__main__":
    unittest.main()
