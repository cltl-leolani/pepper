from pepper.brain import LongTermMemory
from pepper.framework.application.component import AbstractComponent


class BrainComponent(AbstractComponent):
    """
    Proxies the Brain for Responders.
    """

    def __init__(self):
        # type: () -> None
        super(BrainComponent, self).__init__()

    @property
    def brain(self):
        """
        Brain associated with Application

        Returns
        -------
        brain: LongTermMemory
        """
        return super(BrainComponent, self).brain
