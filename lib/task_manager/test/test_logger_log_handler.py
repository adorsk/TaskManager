import unittest
import task_manager
import logging
from StringIO import StringIO


class LoggerLogHandlerTestCase(unittest.TestCase):

    def test_logger_log_handler(self):

        mock_file = StringIO()
        l1 = logging.getLogger('logger1')
        h1 = logging.StreamHandler(mock_file)
        h1.setFormatter(logging.Formatter('l1: %(message)s'))
        l1.addHandler(h1)
        l1.setLevel(logging.DEBUG)

        l2 = logging.getLogger('logger2')
        h2 = task_manager.LoggerLogHandler(l1)
        h2.setFormatter(logging.Formatter('l2: %(message)s'))
        l2.addHandler(h2)
        l2.setLevel(logging.DEBUG)

        l2.debug('testo')
        self.assertEqual('l1: l2: testo\n', mock_file.getvalue())

if __name__ == "__main__":
    unittest.main()
