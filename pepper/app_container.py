from pepper import logger, ApplicationBackend
from pepper.framework.config.local import LocalConfigurationContainer
from pepper.framework.event.memory import SynchronousEventBusContainer
from pepper.framework.resource.threaded import ThreadedResourceContainer
from pepper.framework.sensor.container import DefaultSensorContainer


# TODO Load configuration from application once we don't use inheritance anymore for components
LocalConfigurationContainer.load_configuration()
application_backend = LocalConfigurationContainer.get_config("DEFAULT", "backend")


if application_backend is ApplicationBackend.SYSTEM:
    from pepper.framework.backend.system import SystemBackendContainer as backend_container
elif application_backend is ApplicationBackend.NAOQI:
    from pepper.framework.backend.naoqi import NAOqiBackendContainer as backend_container
else:
    raise ValueError("Unknown backend configured: " + str(application_backend))


class ApplicationContainer(backend_container, DefaultSensorContainer, SynchronousEventBusContainer,
                           ThreadedResourceContainer, LocalConfigurationContainer):
    logger.info("Initialized ApplicationContainer")
