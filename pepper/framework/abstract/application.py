import logging
from logging import Logger
from time import sleep

from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.backend.abstract.led import AbstractLed
from pepper.framework.backend.abstract.motion import AbstractMotion
from pepper.framework.backend.abstract.tablet import AbstractTablet

logger = logging.getLogger(__name__)


# TODO replace components by events

class AbstractApplication(AbstractComponent):
    """
    The Application class is at the base of every robot application.
    It keeps track of events from different instances of :class:`~pepper.framework.abstract.component.AbstractComponent`,
    allows extension by instances of :class:`~pepper.framework.abstract.intention.AbstractIntention` and
    exposes :class:`~pepper.framework.backend.abstract.AbstractBackend` devices to the Application Layer.
    """

    _EVENT_TAG = 'on_'

    def __init__(self):
        super(AbstractApplication, self).__init__()

        # Instantiate Logger for this Application
        self._log = logger.getChild(self.__class__.__name__)

        # Find Events associated with Application (inherited from Components)
        self._events = {k: v for k, v in self.__dict__.items() if k.startswith(self._EVENT_TAG) and callable(v)}

        self.log.info("Booted Application")

    def start(self):
        try:
            self.backend.start()
            super(AbstractApplication, self).start()
        except:
            self.stop()

    def stop(self):
        try:
            super(AbstractApplication, self).stop()
        finally:
            self.backend.stop()

    @property
    def log(self):
        # type: () -> Logger
        """
        Returns Application `Logger <https://docs.python.org/2/library/logging.html>`_

        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def motion(self):
        # type: () -> AbstractMotion
        """
        Returns :class:`~pepper.framework.backend.abstract.motion.AbstractMotion` associated with current Backend

        Returns
        -------
        motion: AbstractMotion
        """
        return self.backend.motion

    @property
    def led(self):
        # type: () -> AbstractLed
        """
        Returns :class:`~pepper.framework.backend.abstract.led.AbstractLed` associated with current Backend

        Returns
        -------
        motion: AbstractMotion
        """
        return self.backend.led

    @property
    def tablet(self):
        # type: () -> AbstractTablet
        """
        Returns :class:`~pepper.framework.backend.abstract.tablet.AbstractTablet` associated with current Backend

        Returns
        -------
        tablet: AbstractTablet
        """
        return self.backend.tablet

    def run(self):
        """
        Run Application

        Starts Camera & Microphone and Blocks Current Thread until KeyboardInterrupt
        """
        self.start()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            pass

        self.stop()

        exit(0)

    def _reset_events(self):
        """
        Reset Event Callbacks to their (unimplemented) defaults

        Used when the Application Switches between AbstractIntention, to remove links to the old AbstractIntention
        """
        for event_name, event_function in self._events.items():
            self.__setattr__(event_name, event_function)

        #TODO Unregister event handlers from EventBus
