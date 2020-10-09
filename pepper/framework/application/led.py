from enum import Enum
from typing import List, Tuple

from pepper.framework.application.component import AbstractComponent
from pepper.framework.backend.abstract.led import Led
from pepper.framework.backend.abstract.led import TOPIC
from pepper.framework.infra.event.api import Event


class LedComponent(AbstractComponent):
    """Control Robot LEDs"""
    def __init__(self):
        # type: () -> None
        super(LedComponent, self).__init__()

        self._log.info("Initializing LedComponent")

    def activate_led(self, leds, rgb, duration):
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
        event = Event({'activate': True, 'leds': leds, 'rgb': rgb, 'duration': duration}, None)
        self.event_bus.publish(TOPIC, event)

    def deactivate_led(self, leds):
        # type: (List[Led]) -> None
        """
        Switch LEDs off

        Parameters
        ----------
        leds: List[Led]
            Which LEDs are affected
        """
        event = Event({'activate': False, 'leds': leds}, None)
        self.event_bus.publish(TOPIC, event)

