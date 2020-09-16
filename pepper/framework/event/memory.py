import logging
from threading import RLock

from pepper.framework.di_container import singleton
from pepper.framework.event.api import *

logger = logging.getLogger(__name__)


class SynchronousEventBusContainer(EventBusContainer):
    logger.info("Initialized SynchronousEventBusContainer")
    @property
    @singleton
    def event_bus(self):
        return SynchronousEventBus()


class SynchronousEventBus(EventBus):
    def __init__(self):
        self._handlers = {}
        self._topic_lock = RLock()

    def publish(self, topic, event, async=False, timeout=-1):
        for handler in self.__get_handlers(topic):
            handler(event)

    def subscribe(self, topic, handler):
        with self._topic_lock:
            self.__get_handlers(topic).append(handler)

    def unsubscribe(self, topic, handler):
        with self._topic_lock:
            if handler:
                self.__get_handlers(topic).remove(handler)
            else:
                self.__get_handlers(topic).clear()

    @property
    def topics(self):
        with self._topic_lock:
            return self._handlers.keys()

    def __get_handlers(self, topic):
        with self._topic_lock:
            if topic not in self._handlers:
                self._handlers[topic] = []

            return self._handlers[topic]