import logging
from threading import Thread
from time import sleep

from pepper.framework.application.intention import AbstractIntention
from pepper.framework.backend.container import BackendContainer

logger = logging.getLogger(__name__)


class AbstractApplication(BackendContainer):
    def __init__(self, intention):
        # type: (AbstractIntention) -> None
        super(AbstractApplication, self).__init__()
        intention.on_intention_change = self.__change_intention
        self._intention = intention

    def __start(self):
        try:
            self.backend.start()
            self._intention.start()
        except:
            logger.exception("Failed to start application")
            self.__stop()

    def __stop(self):
        try:
            self._intention.stop()
        finally:
            self.backend.stop()

    def __change_intention(self, new_intention):
        # Run this asynchronous, as it will be executed from a worker thread which we attempt to stop during the change
        Thread(target=lambda: self.__run_change_intention(new_intention)).start()

    def __run_change_intention(self, new_intention):
        logger.info("<- Switching Intention")
        self._intention.stop()
        self._intention = new_intention
        self._intention.on_intention_change = self.__change_intention
        self._intention.start()
        logger.info("<- Switched Intention")

    def run(self):
        """
        Run Application

        Starts Camera & Microphone and Blocks Current Thread until KeyboardInterrupt
        """
        self.__start()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            pass

        self.__stop()

        exit(0)
