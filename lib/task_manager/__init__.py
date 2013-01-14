"""
Utilities for working with tasks.
"""

from blinker import Signal
import logging


class TaskMessageLogHandler(logging.Handler):
    """ Custom log handler that saves log messages
    to a task's 'message' attribute. """
    def __init__(self, task=None, **kwargs):
        logging.Handler.__init__(self, **kwargs)
        self.task = task
    def emit(self, record):
        try:
            self.task.message = self.format(record)
        except:
            self.handleError(record)
            
class TaskProgressLogHandler(logging.Handler):
    """ Custom log handler that updates a task's 
    'progress' attribute. """
    def __init__(self, task=None, **kwargs):
        logging.Handler.__init__(self, **kwargs)
        self.task = task
    def emit(self, record):
        try:
            self.task.progress = float(self.format(record))
        except:
            self.handleError(record)

class LoggerLogHandler(logging.Handler):
    """ Custom log handler that logs messages to another
    logger. This can be used to chain together loggers. """
    def __init__(self, logger=None, **kwargs):
        logging.Handler.__init__(self, **kwargs)
        self.logger = logger

    def emit(self, record):
        self.logger.log(record.levelno, self.format(record))

def get_message_logger(task, **kwargs):
    logger = logging.getLogger('task_msg_%s' % id(task))
    logger.addHandler(TaskMessageLogHandler(task))
    logger.setLevel(logging.INFO)
    return logger

def get_progress_logger(task, **kwargs):
    logger = logging.getLogger('task_progress_%s' % id(task))
    logger.addHandler(TaskProgressLogHandler(task))
    logger.setLevel(logging.INFO)
    return logger

class Task(object):
    """ A basic task object. """

    # Create some attributes as properties to allow for instrumentation later.
    # This is intended primarily for signaling.
    _task_properties = ['status', 'data', 'progress', 'message', 'errors']

    def __init__(self, *args, **kwargs):
        self.logger = kwargs.get('logger', logging.getLogger())
        for p in self._task_properties:
            setattr(self, "_%s" % p, kwargs.get(p, None))
        if not getattr(self, 'errors'):
            self.errors = []

    def get_message_log_handler(self):
        return TaskMessageLogHandler(self)

    @classmethod
    def add_property(cls, attr):
        def fget(self):
            return getattr(self, "_%s" % attr)
        def fset(self, value):
            setattr(self, "_%s" % attr, value)
        def fdel(self, value):
            delattr(self, "_%s" % attr)

        setattr(cls, attr, property(fget, fset, fdel))

    def call(self):
        pass

    def to_dict(self):
        task_dict = {}
        for p in self._task_properties:
            task_dict[p] = getattr(self, p, None)
        return task_dict

# Add in the properties.
for p in Task._task_properties:
    Task.add_property(p)

def get_signaling_task_class(task_class):
    """ Get a subclass of a task class that will send signals when its
    task properties are set."""

    signaling_task_class = type("Instrumented%s" % task_class.__name__,
                                (task_class,), {})

    signaling_task_class.on_set = Signal()

    # Override property set methods to signal when property is set.
    for pname in task_class._task_properties:
        prop = getattr(task_class, pname)

        # Note: need to bind values for function.
        def fset(self, value, pname=pname, orig_fset=prop.fset):
            orig_fset(self, value)
            self.on_set.send(self, attr=pname, value=value)

        signaling_prop = property(prop.fget, fset, prop.fdel)
        setattr(signaling_task_class, pname, signaling_prop)

    return signaling_task_class
