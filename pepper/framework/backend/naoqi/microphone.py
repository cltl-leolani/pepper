from pepper.framework.event.api import EventBus
from pepper.framework.abstract.microphone import AbstractMicrophone
from pepper import NAOqiMicrophoneIndex
import numpy as np

import qi

from typing import List, Callable, Tuple


class NAOqiMicrophone(AbstractMicrophone):
    SERVICE = "ALAudioDevice"

    def __init__(self, session, rate, index, event_bus):
        # type: (qi.Session, NAOqiMicrophoneIndex, EventBus) -> None
        """
        Initialize NAOqi Microphone

        Parameters
        ----------
        session: qi.Session
            Qi Application Session
        rate: int
            Microphone rate
        index: NAOqiMicrophoneIndex or int
            Which Microphone to Use
        event_bus : EventBus
            EventBus for publishing events
        """
        # TODO Is there a reason only to use rear or front mic?
        super(NAOqiMicrophone, self).__init__(
            rate, 4 if index == NAOqiMicrophoneIndex.ALL else 1, event_bus)

        # Register Service and Subscribe this class as callback
        self._service = session.service(NAOqiMicrophone.SERVICE)
        session.registerService(self.__class__.__name__, self)
        self._service.setClientPreferences(self.__class__.__name__, rate, int(index), 0)
        self._service.subscribe(self.__class__.__name__)

        self._log.debug("Booted")

    def processRemote(self, channels, samples, timestamp, buffer):
        # type: (int, int, Tuple[int, int], bytes) -> None
        """
        Process Audio Window from Pepper/Nao

        This function must be exactly called "processRemote", according to NAOqi specifications.

        Make sure this thread is idle to receive calls from NAOqi to 'processRemote', otherwise frames will be dropped!

        Parameters
        ----------
        channels: int
            Number of Channels
        samples: int
            Number of Samples
        timestamp: (int, int)
            seconds, millis since boot
        buffer: bytes
            Audio Buffer
        """
        audio = np.frombuffer(buffer, np.int16)
        self.on_audio(audio)
