from typing import List, Tuple

from pepper.framework.backend.abstract.led import AbstractLed, Led


class SystemLed(AbstractLed):
    """Control Robot LEDs"""

    def __init__(self, event_bus):
        # type: (EventBus) -> None
        super(SystemLed, self).__init__(event_bus)

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
        self._log.info("Activate " + str(leds))

    def off(self, leds):
        # type: (List[Led]) -> None
        """
        Switch LEDs off

        Parameters
        ----------
        leds: List[Led]
            Which LEDs are affected
        """
        self._log.info("Deactivate " + str(leds))
