import logging
import threading
from queue import Queue, Empty, Full
from threading import Thread
from time import sleep

from enum import Enum
from typing import Iterable, Optional, Union

from pepper.framework.infra.event.api import EventBus, Event, TopicError
from pepper.framework.infra.resource.api import ResourceManager, LockTimeoutError

logger = logging.getLogger(__name__)


_DEPENDENCY_TIMEOUT = 10


class RejectionStrategy(Enum):
    OVERWRITE = 0
    DROP = 1
    BLOCK = 2
    EXCEPTION = 2


class TopicWorker(Thread):
    """
    Process events on a topic from the event bus.
    """

    def __init__(self, topics, event_bus, interval=0, scheduled=None, name=None,
                 buffer_size=1, rejection_strategy=RejectionStrategy.OVERWRITE,
                 resource_manager=None, requires=(), provides=()):
        # type: (Union[str, Iterable[str]], EventBus, float, float, str, int, RejectionStrategy, ResourceManager, Iterable[str], Iterable[str]) -> None
        """
        Parameters
        ----------
        topics : str
        event_bus : EventBus
        interval : float
        scheduled : bool
        name : str
        buffer_size : int
        rejection_strategy : RejectionStrategy
        resource_manager : ResourceManager
        requires : Iterable[str]
        provides : Iterable[str]
        """
        super(TopicWorker, self).__init__(name=name if name else self.__class__.__name__)
        self._event_bus = event_bus
        self._topics = topics if not isinstance(topics, str) else (topics,)
        self._interval = interval
        self._scheduled = scheduled
        self._buffer = Queue(maxsize=buffer_size)
        self._strategy = rejection_strategy
        self._resource_manager = resource_manager
        self._requires = requires
        self._provides = provides
        self._started = threading.Event()
        self._running = False
        self._stop_event = None # type: threading.Event

    def start(self):
        # type: () -> threading.Event
        logger.debug("Starting topic worker %s", self.name)

        super(TopicWorker, self).start()

        return self._started

    def stop(self):
        # type: () -> None
        for topic in self._topics:
            try:
                self._event_bus.unsubscribe(topic, self.__accept_event)
            except:
                logger.exception("Failed to unsubscribe " + self.name + " from " + topic)

        self._running = False
        self._stop_event = threading.Event()
        logger.debug("Stopping topic worker %s", self.name)

    def await_stop(self):
        if not self._stop_event:
            raise ValueError("Worker " + self.name + " is not stopped")

        self._stop_event.wait(_DEPENDENCY_TIMEOUT)

    def run(self):
        self.__resolve_dependencies()
        self._running = True

        for topic in self._topics:
            self._event_bus.subscribe(topic, self.__accept_event)

        self._started.set()

        logger.debug("Started topic worker %s", self.name)

        while self._running:
            self.__process_event()
            if self._interval:
                sleep(self._interval)

        if self._stop_event:
            self._stop_event.set()
        logger.debug("Stopped topic worker %s", self.name)

    def __process_event(self):
        try:
            block = self._interval == 0
            timeout = self._scheduled if self._scheduled else 1  # Never block forever
            self.process(self._buffer.get(block=block, timeout=timeout))
        except Empty:
            if self._scheduled:
                self.process(None)
        except:
            logger.exception("Error during thread execution (%s)", self.name)

    def __accept_event(self, event):
        handled = False
        while not handled:
            try:
                self._buffer.put(event, block=self._strategy == RejectionStrategy.BLOCK)
                handled = True
            except Full as e:
                if self._strategy == RejectionStrategy.EXCEPTION:
                    raise e

                if self._strategy == RejectionStrategy.OVERWRITE:
                    try:
                        self._buffer.get(block=False)
                    except Empty:
                        pass
                elif self._strategy == RejectionStrategy.DROP:
                    handled = True
                else:
                    raise ValueError("Unknown strategy: " + str(self._strategy))

    def __resolve_dependencies(self):
        if self._resource_manager:
            for required in self._requires:
                try:
                    self._resource_manager.get_read_lock(required, timeout=_DEPENDENCY_TIMEOUT)
                except LockTimeoutError as e:
                    raise TopicError(self.name + " failed to obtain required topic: " + required)

            for provided in self._provides:
                try:
                    self._resource_manager.provide_resource(provided)
                except ValueError:
                    # Ignore error if resource is already provided
                    pass

    def process(self, event):
        # type: (Optional[Event]) -> None
        pass

    @property
    def event_bus(self):
        # type: () -> EventBus
        return self._event_bus
