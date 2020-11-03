from threading import Lock
from time import sleep

_MAX_WAIT = 1000


class DIContainer(object):
    """
    Base class for Dependency Injection containers.

    DIContainers manage object creation (injecting necessary dependencies) and
    their life-cycle.
    """
    _lock = Lock()
    _singletons = dict()


def singleton_for_kw(keys):
    """
    Decorator to provide singleton instances from methods of a DIContainer for
    each distinct value of the keyword argument name.
    """
    def plain_singleton(method):
        def decorated(self, *args, **kwargs):
            prefix_values = [kwargs[k] for k in keys if k in kwargs and kwargs[k]]
            prefix = "_".join(prefix_values) + "_" if keys else ""
            singleton_attr = "_" + prefix + method.__name__
            if not singleton_attr in DIContainer._singletons:
                create_instance = False
                with self._lock:
                    if not singleton_attr in DIContainer._singletons:
                        #First set to None and then instantiate outside the lock to avoid dead-locks
                        DIContainer._singletons[singleton_attr] = None
                        create_instance = True
                if create_instance:
                    instance = method(self, *args, **kwargs)
                    if not instance:
                        raise ValueError("could not set " + singleton_attr)
                    DIContainer._singletons[singleton_attr] = instance

            cnt = 0
            # The instance is created outside the lock, therefore we can end up here with None
            while DIContainer._singletons[singleton_attr] is None:
                sleep(0.01)
                cnt += 1
                if cnt > _MAX_WAIT:
                    raise ValueError("Timed out setting " + singleton_attr)

            return DIContainer._singletons[singleton_attr]

        return decorated

    return plain_singleton


singleton = singleton_for_kw([])
"""
Decorator to provide singleton instances from methods of a DIContainer.
"""