import logging
from logging import Logger
from threading import Thread
from time import sleep

from pepper.framework.application.intention import AbstractIntention
from pepper.framework.backend.container import BackendContainer

logger = logging.getLogger(__name__)


# TODO replace components by events

class AbstractApplication(BackendContainer):
    """
    The Application class is at the base of every robot application.
    It keeps track of events from different instances of :class:`~pepper.framework.application.component.AbstractComponent`,
    allows extension by instances of :class:`~pepper.framework.application.intention.AbstractIntention` and
    exposes :class:`~pepper.framework.backend.abstract.AbstractBackend` devices to the Application Layer.
    """

    def __init__(self, intention):
        # type: (AbstractIntention) -> None
        super(AbstractApplication, self).__init__()
        intention.on_intention_change = self._change_intention
        self._intention = intention

    def start(self):
        try:
            self.backend.start()
            self._intention.start()
        except:
            logger.exception("Failed to start application")
            self.stop()

    def stop(self):
        try:
            self._intention.stop()
        finally:
            self.backend.stop()

    def _change_intention(self, new_intention):
        # Run this asynchronous, as it will be executed from a worker thread which we attempt to stop during the change
        Thread(target=lambda: self._run_change_intention(new_intention)).start()

    def _run_change_intention(self, new_intention):
        logger.info("<- Switching Intention")
        self._intention.stop()
        self._intention = new_intention
        self._intention.on_intention_change = self._change_intention
        self._intention.start()
        logger.info("<- Switched Intention")

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
