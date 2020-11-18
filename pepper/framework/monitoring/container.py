import logging
from threading import Thread

from pepper.framework.context.api import ContextContainer
from pepper.framework.infra.di_container import DIContainer, singleton
from pepper.framework.infra.event.api import EventBusContainer
from pepper.framework.infra.resource.api import ResourceContainer
from pepper.framework.infra.topic_worker import TopicWorker
from pepper.framework.monitoring.server.server import MonitoringServer
from pepper.framework.monitoring.worker.monitoring import MonitoringWorker

logger = logging.getLogger(__name__)


class MonitoringWorkerContainer(DIContainer):
    def start_monitoring(self):
        raise NotImplementedError("Monitoring worker not configured")

    def stop(self):
        try:
            super(MonitoringWorkerContainer, self).stop()
        except AttributeError:
            # Ignore if the container is on top of the MRO
            pass


class DefaultMonitoringWorkerContainer(MonitoringWorkerContainer, ContextContainer, EventBusContainer, ResourceContainer):
    __worker = None  # type: TopicWorker

    def start_monitoring(self):
        server = self._monitoring_server
        DefaultMonitoringWorkerContainer.__worker = MonitoringWorker(self.context, server, "MonitoringWorker",
                                                                     self.event_bus, self.resource_manager)

        return (DefaultMonitoringWorkerContainer.__worker.start(),)

    @property
    @singleton
    def _monitoring_server(self):
        server = MonitoringServer()
        DefaultMonitoringWorkerContainer.__server = server

        server_thread = Thread(target=server.start, name="DisplayServerThread")
        server_thread.daemon = True
        server_thread.start()

        return server

    def stop(self):
        logger.debug("Stopping workers")

        try:
            DefaultMonitoringWorkerContainer.__worker.stop()
        finally:
            super(DefaultMonitoringWorkerContainer, self).stop()

        DefaultMonitoringWorkerContainer.__worker.await_stop()

        logger.debug("Stopped workers")
