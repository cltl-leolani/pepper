# TODO Load configuration from application once we don't use inheritance anymore for components
import logging.config

from pepper.brain.long_term_memory import BrainContainer, LongTermMemory
from pepper.framework.context.container import DefaultContextContainer, DefaultContextWorkerContainer
from pepper.framework.infra.di_container import singleton

logging.config.fileConfig('config/logging.config')

from pepper import ApplicationBackend
from pepper.framework.infra.config.local import LocalConfigurationContainer
from pepper.framework.infra.event.memory import SynchronousEventBusContainer
from pepper.framework.infra.resource.threaded import ThreadedResourceContainer
from pepper.framework.sensor.container import DefaultSensorContainer, DefaultSensorWorkerContainer

logger = logging.getLogger(__name__)


# TODO Load configuration from application once we don't use inheritance anymore for components
LocalConfigurationContainer.load_configuration()
_application_backend = ApplicationBackend[LocalConfigurationContainer.get_config("DEFAULT", "backend").upper()]


if _application_backend is ApplicationBackend.SYSTEM:
    from pepper.framework.backend.system.backend import SystemBackendContainer as backend_container
elif _application_backend is ApplicationBackend.NAOQI:
    from pepper.framework.backend.naoqi import NAOqiBackendContainer as backend_container
else:
    raise ValueError("Unknown backend configured: " + str(_application_backend))


class ApplicationContainer(backend_container,
                           DefaultSensorWorkerContainer, DefaultSensorContainer,
                           DefaultContextWorkerContainer, DefaultContextContainer,
                           SynchronousEventBusContainer, ThreadedResourceContainer, LocalConfigurationContainer,
                           BrainContainer):

    logger.info("Initialized ApplicationContainer")

    @property
    @singleton
    def brain(self):
        config = self.config_manager.get_config("pepper.framework.component.brain")
        url = config.get("url")
        log_dir = config.get("log_dir")

        return LongTermMemory(url, log_dir)