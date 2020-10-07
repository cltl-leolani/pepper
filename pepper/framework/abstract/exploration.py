from pepper.framework.abstract.component import AbstractComponent


class ExplorationComponent(AbstractComponent):
    def __init__(self):
        # type: () -> None
        super(ExplorationComponent, self).__init__()

        self._log.info("Initializing ExplorationComponent")

    def start(self):
        self.start_exploration_worker()

        super(ExplorationComponent, self).start()

    def stop(self):
        super(ExplorationComponent, self).stop()