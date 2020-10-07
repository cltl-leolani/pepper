# TODO Load configuration from application once we don't use inheritance anymore for components
import logging
import logging.config
import os

from pepper.framework.context import ContextContainer, Context
from pepper.framework.di_container import singleton

logging.config.fileConfig('config/logging.config')


from pepper import ApplicationBackend
from pepper.framework.config.local import LocalConfigurationContainer
from pepper.framework.event.memory import SynchronousEventBusContainer
from pepper.framework.resource.threaded import ThreadedResourceContainer
from pepper.framework.sensor.container import DefaultSensorContainer


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


class ApplicationContainer(backend_container, DefaultSensorContainer, SynchronousEventBusContainer,
                           ThreadedResourceContainer, LocalConfigurationContainer,
                           ContextContainer):

    logger.info("Initialized ApplicationContainer")

    @property
    @singleton
    def context(self):
        configuration = self.config_manager.get_config("pepper.framework.component.context")
        name = configuration.get("name")
        friends_dir = configuration.get("friends_dir")

        # Initialize the Context for this Application
        friends = [os.path.splitext(path)[0] for path in os.listdir(friends_dir) if path.endswith(".bin")]

        return Context(name, friends)

