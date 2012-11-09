from threading import Timer
import time
import daemon
import sys
import json
import httplib2
import logging
import importlib
import select
import task_manager


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PostingTaskRunner(object):
    def __init__(self, post_url=None, delay=5, **kwargs):
        self.post_url = post_url
        self.delay = delay
        self.timers = {}
        self.http = httplib2.Http()
        self.headers = {'Content-type': 'application/json'}

    def run_task(self, task):
        logger.debug('run_task %s' % task)
        task.on_set.connect(self.on_task_update)
        try:
            task.call()
        except Exception as e:
            error = "Error running: %s" % e
            logger.debug(error)
            logger.exception()
            task.errors.append(error)
            task.status = "rejected"

    def on_task_update(self, task, **kwargs):
        timer = self.timers.get(task)
        if timer:
            timer.cancel()
        self.timers[task] = Timer(self.delay, self.post_task,
                                  kwargs={'task': task})
        self.timers[task].start()

    def post_task(self, task=None):
        logger.debug('posting, task is: %s' % task.to_dict())
        logger.debug('post url is: %s' % self.post_url)
        logger.debug('post data is: %s' % task.to_dict())
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

        # Instrument the task class to send signals.
        SignalingTaskClass = task_manager.get_signaling_task_class(TaskClass)

        task_args = task_config.get('args', [])
        task_kwargs = task_config.get('kwargs', {})
        task_kwargs['logger'] = logger
        task = SignalingTaskClass(*task_args, **task_kwargs)
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
