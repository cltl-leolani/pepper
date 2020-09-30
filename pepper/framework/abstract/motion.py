from typing import Tuple

from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.backend.abstract.motion import TOPIC_LOOK
from pepper.framework.backend.abstract.motion import TOPIC_POINT
from pepper.framework.event.api import Event


class MotionComponent(AbstractComponent):
    """Control Robot Motion (other than speech animation)"""

    def __init__(self):
        # type: () -> None
        super(MotionComponent, self).__init__()

        self._log.info("Initializing MotionComponent")

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
        event = Event({'direction': direction, 'speed': speed}, None)
        self.event_bus.publish(TOPIC_LOOK, event)

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
        event = Event({'direction': direction, 'speed': speed}, None)
        self.event_bus.publish(TOPIC_POINT, event)
