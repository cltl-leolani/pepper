from pepper.framework.application.component import AbstractComponent


class ExplorationComponent(AbstractComponent):
    def __init__(self):
        # type: () -> None
        super(ExplorationComponent, self).__init__()

        self._log.info("Initializing ExplorationComponent")

    def start(self):
        started_events = self.start_exploration_worker()

        super(ExplorationComponent, self).start()

        timeout = self.config_manager.get_config("DEFAULT").get_float("dependency_timeout")
        for event in started_events:
            event.wait(timeout=timeout)

    def stop(self):
        super(ExplorationComponent, self).stop()