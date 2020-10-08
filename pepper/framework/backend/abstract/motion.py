import logging

from typing import Tuple

from pepper.framework.event.api import EventBus
from pepper.framework.resource.api import ResourceManager

logger = logging.getLogger(__name__)


TOPIC_POINT = "pepper.framework.backend.abstract.motion.point"
TOPIC_LOOK = "pepper.framework.backend.abstract.motion.look"


class AbstractMotion(object):
    """Control Robot Motion (other than speech animation)"""

    def __init__(self, event_bus, resource_manager):
        # type: (EventBus, ResourceManager) -> None
        self._log = logger.getChild(self.__class__.__name__)

        event_bus.subscribe(TOPIC_POINT, self._point_handler)
        event_bus.subscribe(TOPIC_LOOK, self._look_handler)
        resource_manager.provide_resource(TOPIC_POINT)
        resource_manager.provide_resource(TOPIC_LOOK)

    def _look_handler(self, event):
        payload = event.payload
        direction = payload['direction']
        speed = payload['speed']

        self.look(direction, speed)

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
        raise NotImplementedError()

    def _point_handler(self, event):
        payload = event.payload
        direction = payload['direction']
        speed = payload['speed']

        self.point(direction, speed)

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
        raise NotImplementedError()
