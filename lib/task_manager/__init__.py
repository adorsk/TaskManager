"""
Utilities for working with tasks.
"""

from blinker import Signal
import logging


class Task(object):
    """ A basic task object. """

    # Create some attributes as properties to allow for instrumentation later.
    # This is intended primarily for signaling.
    _task_properties = ['status', 'data']

    def __init__(self, logger=logging.getLogger(), **kwargs):
        self.logger = logger
        for p in self._task_properties:
            setattr(self, "_%s" % p, kwargs.get(p, None))

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
