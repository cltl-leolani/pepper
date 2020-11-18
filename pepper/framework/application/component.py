import logging
from logging import Logger

from typing import ClassVar

from pepper.brain.long_term_memory import BrainContainer
from pepper.framework.backend.abstract.backend import AbstractBackend
from pepper.framework.backend.container import BackendContainer
from pepper.framework.infra.config.api import ConfigurationContainer
from pepper.framework.context.api import ContextContainer, ContextWorkerContainer
from pepper.framework.infra.event.api import EventBusContainer
from pepper.framework.monitoring.container import MonitoringWorkerContainer
from pepper.framework.infra.resource.api import ResourceContainer
from pepper.framework.sensor.api import SensorContainer, SensorWorkerContainer

logger = logging.getLogger(__name__)


# TODO For now use the mixin pattern, unify dependency management
class AbstractComponent(MonitoringWorkerContainer, BackendContainer,
                        ContextWorkerContainer, ContextContainer,
                        SensorWorkerContainer, SensorContainer,
                        BrainContainer,
                        EventBusContainer, ResourceContainer, ConfigurationContainer):
    """
    Abstract Base Component on which all Components are Based

    Parameters
    ----------
    backend: AbstractBackend
        Application :class:`~pepper.framework.backend.abstract.backend.AbstractBackend`
    """

    def __init__(self):
        # type: () -> None
        super(AbstractComponent, self).__init__()

        self._log = logger.getChild(self.__class__.__name__)
        self._log.debug("Initializing")

    def start(self):
        pass

    def stop(self):
        super(AbstractComponent, self).stop()

    @property
    def log(self):
        # type: () -> Logger
        """
        Returns Component `Logger <https://docs.python.org/2/library/logging.html>`_

        Returns
        -------
        logger: logging.Logger
        """
        return self._log