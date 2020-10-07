from pepper.framework.abstract.component import AbstractComponent


class ExplorationComponent(AbstractComponent):
    def __init__(self):
        # type: () -> None
        super(ExplorationComponent, self).__init__()

        self._log.info("Initializing ContextComponent")

    def start(self):
        self.start_exploration_workers()

        super(ExplorationComponent, self).start()

    def stop(self):
        super(ExplorationComponent, self).stop()