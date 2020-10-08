from threading import Thread

from pepper.framework.context.api import ContextContainer
from pepper.framework.di_container import DIContainer
from pepper.framework.monitoring.server.server import MonitoringServer
from pepper.framework.monitoring.worker.monitoring import MonitoringWorker


class MonitoringContainer(DIContainer):
    def start_monitoring(self):
        raise NotImplementedError("Monitoring worker not configured")

    def stop(self):
        try:
            super(MonitoringContainer, self).stop()
        except AttributeError:
            # Ignore if the container is on top of the MRO
            pass


class DefaultMonitoringContainer(MonitoringContainer, ContextContainer):
    __server = None
    __worker = None

    def start_monitoring(self):
        server = MonitoringServer()
        DefaultMonitoringContainer.__server = server

        server_thread = Thread(target=server.start, name="DisplayServerThread")
        server_thread.daemon = True
        server_thread.start()

        DefaultMonitoringContainer.__worker = MonitoringWorker(self.context, server, "MonitoringWorker",
                                                               self.event_bus, self.resource_manager)
        DefaultMonitoringContainer.__worker.start()

    def stop(self):
        try:
            DefaultMonitoringContainer.__server.stop()
            DefaultMonitoringContainer.__worker.stop()
        finally:
            super(DefaultMonitoringContainer, self).stop()
