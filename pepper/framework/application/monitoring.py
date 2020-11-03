from pepper.framework.application.component import AbstractComponent


class MonitoringComponent(AbstractComponent):
    def __init__(self):
        # type: () -> None
        super(MonitoringComponent, self).__init__()

        self._log.info("Initializing MonitoringComponent")

    def start(self):
        started_events = self.start_monitoring()

        super(MonitoringComponent, self).start()

        timeout = self.config_manager.get_config("DEFAULT").get_float("dependency_timeout")
        for event in started_events:
            event.wait(timeout=timeout)

    def stop(self):
        super(MonitoringComponent, self).stop()