import logging
import os
import threading
from Queue import Queue
from typing import Iterable, Any

from pepper.framework.infra.config.api import ConfigurationContainer
from pepper.framework.context.api import ContextContainer, Context, ContextWorkerContainer
from pepper.framework.context.worker.context import ContextWorker
from pepper.framework.context.worker.exploration import ExplorationWorker
from pepper.framework.infra.di_container import singleton
from pepper.framework.infra.event.api import EventBusContainer
from pepper.framework.infra.resource.api import ResourceContainer
from pepper.framework.infra.topic_worker import TopicWorker

logger = logging.getLogger(__name__)


class DefaultContextContainer(ContextContainer, ConfigurationContainer):
    @property
    @singleton
    def context(self):
        configuration = self.config_manager.get_config("pepper.framework.component.context")
        name = configuration.get("name")
        friends_dir = configuration.get("friends_dir")

        # Initialize the Context for this Application
        friends = [os.path.splitext(path)[0] for path in os.listdir(friends_dir) if path.endswith(".bin")]

        return Context(name, friends)


class DefaultContextWorkerContainer(ContextWorkerContainer, ContextContainer,
                                    EventBusContainer, ResourceContainer, ConfigurationContainer):

    __workers = Queue()  # type: Queue[TopicWorker]

    def start_context_worker(self):
        # type: () -> Iterable[threading.Event]
        worker = ContextWorker(self.context, "ContextWorker", self.event_bus, self.resource_manager, self.config_manager)
        DefaultContextWorkerContainer.__workers.put(worker)

        return (worker.start(),)

    def start_exploration_worker(self):
        # type: () -> Iterable[threading.Event]
        worker = ExplorationWorker(self.context, "ExplorationWorker", self.event_bus)
        DefaultContextWorkerContainer.__workers.put(worker)

        return (worker.start(),)

    def stop(self):
        logger.info("Stopping workers")

        for worker in self.__workers.queue:
            try:
                worker.stop()
            except:
                logger.exception("Failed to stop worker " + worker.name)

        super(DefaultContextWorkerContainer, self).stop()

        for worker in self.__workers.queue:
            worker.await_stop()
        self.__workers.queue.clear()

        logger.info("Stopped workers")