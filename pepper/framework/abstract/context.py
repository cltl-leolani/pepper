from pepper.framework.abstract.component import AbstractComponent


class ContextComponent(AbstractComponent):
    def __init__(self):
        # type: () -> None
        super(ContextComponent, self).__init__()

        self._log.info("Initializing ContextComponent")

    def start(self):
        self.start_context_workers()

        super(ContextComponent, self).start()

    def stop(self):
        super(ContextComponent, self).stop()