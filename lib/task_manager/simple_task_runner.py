"""
Simple task runner, intended mainly for testing tasks.
"""
from threading import Timer
import time
import daemon
import sys
import json
import logging
import importlib
import select
import task_manager


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class SimpleTaskRunner(object):

    def run_task(self, task):
        logger.debug('run_task %s' % task)
        try:
            task.call()
        except Exception as e:
            error = "Error running: %s" % e
            logger.debug(error)
            logger.exception(error)
            task.errors.append(error)

if __name__ == '__main__':

    logfile = '/tmp/SimpleTaskRunner.log'
    logger.addHandler(logging.FileHandler(logfile))

    try:
        if not select.select([sys.stdin,],[],[],0.0)[0]:
            raise Exception("No input provided on stdin.")
        task_json = sys.stdin.read()
        task_definition = json.loads(task_json)
    except Exception as e:
        logger.exception("Unable to read task definition from stdin.")
        raise e

    # Load the task
    try:
        task_config = task_definition['config']['task']
        class_parts = task_config['class'].split('.')
        module_name = '.'.join(class_parts[:-1])
        class_name = class_parts[-1]
        module = importlib.import_module(module_name)
        TaskClass = getattr(module, class_name)

        task_args = task_config.get('args', [])
        task_kwargs = task_config.get('kwargs', {})
        task_kwargs['logger'] = logger
        task = TaskClass(*task_args, **task_kwargs)
    except:
        logger.exception("Unable to create task.")
        raise

    # Create the runner.
    task_runner = SimpleTaskRunner()

    # If running from tty, use same stdout/stderr.
    if sys.stdin.isatty():
        daemon_stdout = sys.stdout
        daemon_stderr = sys.stderr
    else:
        daemon_stdout = None
        daemon_stderr = None

    # Run task as Daemon.
    with daemon.DaemonContext(
        stdout=daemon_stdout,
        stderr=daemon_stderr,
        files_preserve=[handler.stream for handler in logger.handlers]
    ):
        task_runner.run_task(task)
