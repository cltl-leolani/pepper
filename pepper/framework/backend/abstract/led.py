import logging

from enum import Enum
from typing import List, Tuple

from pepper.framework.infra.event.api import EventBus
from pepper.framework.infra.resource.api import ResourceManager

logger = logging.getLogger(__name__)


TOPIC = "pepper.framework.backend.abstract.led.topic"


class Led(Enum):
    """NAOqi LED ids"""

    LeftEarLeds = 0
    LeftEarLed1 = 1
    LeftEarLed2 = 2
    LeftEarLed3 = 3
    LeftEarLed4 = 4
    LeftEarLed5 = 5
    LeftEarLed6 = 6
    LeftEarLed7 = 7
    LeftEarLed8 = 8
    LeftEarLed9 = 9
    LeftEarLed10 = 10
    RightEarLeds = 11
    RightEarLed1 = 12
    RightEarLed2 = 13
    RightEarLed3 = 14
    RightEarLed4 = 15
    RightEarLed5 = 16
    RightEarLed6 = 17
    RightEarLed7 = 18
    RightEarLed8 = 19
    RightEarLed9 = 20
    RightEarLed10 = 21
    LeftFaceLeds = 22
    LeftFaceLed1 = 23
    LeftFaceLed2 = 24
    LeftFaceLed3 = 25
    LeftFaceLed4 = 26
    LeftFaceLed5 = 27
    LeftFaceLed6 = 28
    LeftFaceLed7 = 29
    LeftFaceLed8 = 30
    RightFaceLeds = 31
    RightFaceLed1 = 32
    RightFaceLed2 = 33
    RightFaceLed3 = 34
    RightFaceLed4 = 35
    RightFaceLed5 = 36
    RightFaceLed6 = 37
    RightFaceLed7 = 38
    RightFaceLed8 = 39


class AbstractLed(object):
    """Control Robot LEDs"""

    def __init__(self, event_bus, resource_manager):
        # type: (EventBus, ResourceManager) -> None
        self._log = logger.getChild(self.__class__.__name__)

        event_bus.subscribe(TOPIC, self._event_handler)
        resource_manager.provide_resource(TOPIC)

    def _event_handler(self, event):
        payload = event.payload
        leds = payload['leds']

        if payload['activate']:
            rgb = payload['rgb']
            duration = payload['duration']
            self.set(leds, rgb, duration)
        else:
            self.off(leds)

    def set(self, leds, rgb, duration):
        # type: (List[Led], Tuple[float, float, float], float) -> None
        """
        Set LEDs to Particular color (interpolating from its current color in 'duration' time)

        Parameters
        ----------
        leds: List[Led]
            Which LEDs are affected
        rgb: Tuple[float, float, float]
            Which color to turn
        duration: float
            How long to take switching this color
        """
        raise NotImplementedError()

    def off(self, leds):
        # type: (List[Led]) -> None
        """
        Switch LEDs off

        Parameters
        ----------
        leds: List[Led]
            Which LEDs are affected
        """
        raise NotImplementedError()
