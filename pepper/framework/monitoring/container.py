from threading import Thread

from pepper.framework.context.api import ContextContainer
from pepper.framework.infra.di_container import DIContainer
from pepper.framework.infra.event.api import EventBusContainer
from pepper.framework.infra.resource.api import ResourceContainer
from pepper.framework.monitoring.server.server import MonitoringServer
from pepper.framework.monitoring.worker.monitoring import MonitoringWorker


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
    __server = None
    __worker = None

    def start_monitoring(self):
        server = MonitoringServer()
        DefaultMonitoringWorkerContainer.__server = server

        server_thread = Thread(target=server.start, name="DisplayServerThread")
        server_thread.daemon = True
        server_thread.start()

        DefaultMonitoringWorkerContainer.__worker = MonitoringWorker(self.context, server, "MonitoringWorker",
                                                                     self.event_bus, self.resource_manager)

        return (DefaultMonitoringWorkerContainer.__worker.start(),)

    def stop(self):
        try:
            DefaultMonitoringWorkerContainer.__server.stop()
            DefaultMonitoringWorkerContainer.__worker.stop()
        finally:
            super(DefaultMonitoringWorkerContainer, self).stop()
