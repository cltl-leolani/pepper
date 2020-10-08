from pepper.framework.backend.abstract.motion import AbstractMotion
from typing import Tuple

from pepper.framework.event.api import Event, EventBus
from pepper.framework.resource.api import ResourceManager


class SystemMotion(AbstractMotion):
    """Control Robot Motion (other than speech animation)"""

    def __init__(self, event_bus, resource_manager):
        # type: (EventBus, ResourceManager) -> None
        super(SystemMotion, self).__init__(event_bus, resource_manager)

    def look(self, direction, speed=1):
        # type: (Tuple[float, float], float) -> None
        """
        Look at particular direction

        Parameters
        ----------
        direction: Tuple[float, float]
            Direction to look at in View Space (Spherical Coordinates)
        speed: float
            Movement Speed [0,1]
        """
        self._log.info("Look at " + str(direction))

    def point(self, direction, speed=1):
        # type: (Tuple[float, float], float) -> None
        """
        Point at particular direction

        Parameters
        ----------
        direction: Tuple[float, float]
            Direction to point at in View Space (Spherical Coordinates)
        speed: float
            Movement Speed [0,1]
        """
        self._log.info("Point at " + str(direction))