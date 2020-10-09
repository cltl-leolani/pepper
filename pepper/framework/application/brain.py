from pepper.brain import LongTermMemory
from pepper.framework.application.component import AbstractComponent


class BrainComponent(AbstractComponent):
    """
    Exposes the Brain (LongTermMemory) to Applications
    """

    def __init__(self):
        # type: () -> None
        super(BrainComponent, self).__init__()

        self._log.info("Initializing BrainComponent")

        config = self.config_manager.get_config("pepper.framework.component.brain")
        url = config.get("url")
        log_dir = config.get("log_dir")

        self._brain = LongTermMemory(url, log_dir)

        self._log.info("Initialized BrainComponent")

    @property
    def brain(self):
        """
        Brain associated with Application

        Returns
        -------
        brain: LongTermMemory
        """
        return self._brain
