import logging
from Queue import Queue, Empty, Full
from threading import Thread
from time import sleep

from enum import Enum
from typing import Iterable

from pepper.framework.event.api import EventBus, EventBusContainer, Event
from pepper.framework.resource.api import ResourceManager, ResourceContainer

logger = logging.getLogger(__name__)

_DEPENDENCY_TIMEOUT = 10


class RejectionStrategy(Enum):
    OVERWRITE = 0
    DROP = 1
    BLOCK = 2
    EXCEPTION = 2


class TopicWorkerContainer(EventBusContainer, ResourceContainer):
    def create_topic_worker(self, topic, callable_,
                 interval=0, name=None,
                 buffer_size=1, rejection_strategy=RejectionStrategy.OVERWRITE,
                 requires=(), provides=()):
        resource_manager = self.resource_manager if requires or provides else None
        return TopicWorker(topic, self.event_bus, interval=interval, name=name,
                           buffer_size=buffer_size, rejection_strategy=rejection_strategy,
                           resource_manager=resource_manager,
                           requires=requires, provides=provides)



class TopicWorker(Thread):
    """
    Process events on a topic from the event bus.
    """

    def __init__(self, topic, event_bus, interval=0, name=None,
                 buffer_size=1, rejection_strategy=RejectionStrategy.OVERWRITE,
                 resource_manager=None, requires=(), provides=()):
        """

        Parameters
        ----------
        topic : str
        event_bus : EventBus
        interval : float
        name : str
        buffer_size : int
        rejection_strategy : RejectionStrategy
        resource_manager : ResourceManager
        requires : Iterable[str]
        provides : Iterable[str]
        """
        # type: (str, EventBus, float, str, int, RejectionStrategy, ResourceManager, Iterable[str], Iterable[str]) -> None
        super(TopicWorker, self).__init__(name=name if name else self.__class__.__name__)
        self._event_bus = event_bus
        self._topic = topic
        self._interval = interval
        self._buffer = Queue(maxsize=buffer_size)
        self._strategy = rejection_strategy
        self._resource_manager = resource_manager
        self._requires = requires
        self._provides = provides
        self._running = False

    def start(self):
        logger.info("Starting topic worker %s", self.name)

        super(TopicWorker, self).start()

        while not self._running:
            sleep(self._interval)

        self._event_bus.subscribe(self._topic, self.__accept_event)

    def stop(self):
        self._running = False
        logger.info("Stopping topic worker %s", self.name)

    def run(self):
        self.__resolve_dependencies()
        self._running = True
        logger.info("Started topic worker %s", self.name)

        while self._running:
            self.__process_event()
            if self._interval:
                sleep(self._interval)
        logger.info("Stopped topic worker %s", self.name)

    def __process_event(self):
        if self._buffer.empty():
            return

        try:
            self.process(self._buffer.get(block=False))
        except Empty:
            pass
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
                self._resource_manager.get_read_lock(required, timeout=_DEPENDENCY_TIMEOUT)
            for provided in self._provides:
                try:
                    self._resource_manager.provide_resource(provided)
                except ValueError:
                    # Ignore error if resource is already provided
                    pass

    def process(self, event):
        # type: (Event) -> None
        pass

    @property
    def event_bus(self):
        return self._event_bus