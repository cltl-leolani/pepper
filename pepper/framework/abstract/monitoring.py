from pepper.framework.abstract.component import AbstractComponent


class MonitoringComponent(AbstractComponent):
    def __init__(self):
        # type: () -> None
        super(MonitoringComponent, self).__init__()

        self._log.info("Initializing MonitoringComponent")

    def start(self):
        self.start_monitoring()

        super(MonitoringComponent, self).start()

    def stop(self):
        super(MonitoringComponent, self).stop()