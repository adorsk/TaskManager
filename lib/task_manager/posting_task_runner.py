from threading import Timer
import time
import daemon
import sys
import json
import httplib2
import logging
import importlib


logger = logging.getLogger(__name__)

class PostingTaskRunner(object):
    def __init__(self, post_url=None, delay=5, **kwargs):
        self.post_url = post_url
        self.delay = delay
        self.timers = {}
        self.http = httplib2.Http()
        self.headers = {'Content-type': 'application/json'}

    def run_task(self, task):
        logger.debug('run_task %s' % task)
        task.on_update.connect(self.on_task_update)
        task.call()

    def on_task_update(self, task):
        timer = self.timers.get(task)
        if timer:
            timer.cancel()
        self.timers[task] = Timer(self.delay, self.post_task,
                                  kwargs={'task': task})
        self.timers[task].start()

    def post_task(self, task=None):
        logger.debug('posting, task is: %s' % task.to_dict())
        logger.debug('post url is: %s' % self.post_url)
        try:
            rh, rc = self.http.request(
                self.post_url,
                'POST', 
                headers=self.headers,
                body=json.dumps(task.to_dict())
            )
            logger.debug('response headers is: %s' % rh)
            logger.debug('response content is: %s' % rc)
        except:
            logger.exception("Posting error.")
            raise

if __name__ == '__main__':

    logfile = '/tmp/PostingTaskRunner.log'
    logger.addHandler(logging.FileHandler(logfile))

    try:
        task_json = sys.stdin.read()
        task_definition = json.loads(task_json)
    except:
        logger.exception("Unable to read task definition from stdin.")

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
        task = TaskClass(*task_args, **task_kwargs)
    except:
        logger.exception("Unable to create task.")
        raise

    # Create the runner.
    post_url = task_definition['config']['update_url']
    task_runner = PostingTaskRunner(post_url=post_url, delay=1)

    # Run task as Daemon.
    with daemon.DaemonContext(
        stdout=sys.stdout,
        files_preserve=[handler.stream for handler in logger.handlers]
    ):
        task_runner.run_task(task)
