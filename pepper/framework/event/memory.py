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
            handler(event.with_topic(topic))

    def subscribe(self, topic, handler):
        with self._topic_lock:
            self.__get_handlers(topic).append(handler)

        logger.info("Subscribed %s to topic %s", self.__format_name(handler), topic)

    def unsubscribe(self, topic, handler):
        with self._topic_lock:
            if handler:
                try:
                    self.__get_handlers(topic).remove(handler)
                except ValueError as e:
                    raise ValueError("Failed to unregister " + self.__format_name(handler), e)
                logger.info("Unsubscribed %s from topic %s", self.__format_name(handler), topic)
            else:
                self.__get_handlers(topic).clear()
                logger.info("Unsubscribed handlers from topic %s", topic)

    @property
    def topics(self):
        with self._topic_lock:
            return self._handlers.keys()

    def __get_handlers(self, topic):
        with self._topic_lock:
            if topic not in self._handlers:
                self._handlers[topic] = []

            return self._handlers[topic]

    def __format_name(self, handler):
        return (handler.im_class.__name__ + "." if hasattr(handler, "im_class") else "") + handler.__name__

