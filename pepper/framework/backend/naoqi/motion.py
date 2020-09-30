from pepper.framework.backend.abstract.motion import AbstractMotion
from pepper.framework.event.api import EventBus
from pepper.framework.util import spherical2cartesian

import qi

import numpy as np

from threading import Thread
from Queue import Queue

from typing import Tuple


class NAOqiMotion(AbstractMotion):
    """
    Control Robot Motion (other than speech animation) through NAOqi Motion

    Parameters
    ----------
    session: qi.Session
        The current session with the Robot
    """

    SERVICE_MOTION = "ALMotion"
    SERVICE_TRACKER = "ALTracker"

    COMMAND_LIMIT = 2  # The maximum number of commands in the queue to prevent blocking all access to robot motion
    FRAME = 0  # 0 = With Respect to Torso

    def __init__(self, session, event_bus):
        # type: (qi.Session, EventBus) -> None
        super(NAOqiMotion, self).__init__(event_bus)

        # Connect to Motion and Tracker Services
        self._motion = session.service(NAOqiMotion.SERVICE_MOTION)
        self._tracker = session.service(NAOqiMotion.SERVICE_TRACKER)

        # Create Thread and Queue for 'look' commands
        self._look_queue = Queue()
        self._look_thread = Thread(target=self._look_worker, name="NAOqiLookThread")
        self._look_thread.daemon = True
        self._look_thread.start()

        # Create Thread and Queue for 'point' commands
        self._point_queue = Queue()
        self._point_thread = Thread(target=self._point_worker, name="NAOqiPointThread")
        self._point_thread.daemon = True
        self._point_thread.start()

    def look(self, event):
        # type: (Event) -> None
        """
        Look at particular direction

        Parameters
        ----------
        direction: Tuple[float, float]
            Direction to look at in View Space (Spherical Coordinates)
        speed: float
            Movement Speed [0,1]
        """
        payload = event.payload
        direction = payload['direction']
        speed = payload['speed']

        if self._look_queue.qsize() < NAOqiMotion.COMMAND_LIMIT:
            self._look_queue.put((direction, speed))

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
        if self._point_queue.qsize() < NAOqiMotion.COMMAND_LIMIT:
            self._point_queue.put((direction, speed))

    def _look(self, direction, speed=1):
        # type: (Tuple[float, float], float) -> None

        # Translate direction to xyz and look at that xyz
        self._tracker.lookAt(self._dir2xyz(direction), NAOqiMotion.FRAME, float(np.clip(speed, 0, 1)), False)

    def _point(self, direction, speed=1):
        # type: (Tuple[float, float], float) -> None

        # Translate direction to xyz
        coordinates = self._dir2xyz(direction)

        # Point with Left/Right arm to Left/Right targets
        lr = "L" if coordinates[1] > 0 else "R"

        # point higher... (seems hacky)
        coordinates[2] += 1

        # Point with correct arm to target
        self._tracker.pointAt("{}Arm".format(lr), coordinates, NAOqiMotion.FRAME, float(np.clip(speed, 0, 1)))

        # Open hand to 'point' very convincingly
        self._motion.openHand("{}Hand".format(lr))

        # Keep arm pointed at object a little longer
        self._tracker.pointAt("{}Arm".format(lr), coordinates, NAOqiMotion.FRAME, float(np.clip(speed, 0, 1)))

    def _dir2xyz(self, direction):

        # Translate Direction to X,Y,Z coordinate (with arbitrary depth) to smooth NAOqi API interfacing
        x, z, y = spherical2cartesian(-direction[0], direction[1], 5)
        return [float(x), float(y), float(z)]

    def _look_worker(self):
        # Execute whatever is on the Look Queue
        while True: self._look(*self._look_queue.get())

    def _point_worker(self):
        # Execute whatever is on the Point Queue
        while True: self._point(*self._point_queue.get())
