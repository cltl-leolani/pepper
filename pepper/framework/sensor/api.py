from Queue import Queue

import numpy as np
from typing import Iterable

from pepper.framework.di_container import DIContainer
from pepper.framework.multiprocessing import TopicWorker
from pepper.framework.util import Bounds
# Include from submodules
# noinspection PyUnresolvedReferences
from .asr import AbstractASR, AbstractTranslator, UtteranceHypothesis
# noinspection PyUnresolvedReferences
from .location import Location
# noinspection PyUnresolvedReferences
from .obj import Object


class SensorContainer(DIContainer):
    def asr(self, language=None):
        raise ValueError("ASR not configured")

    @property
    def vad(self):
        # type: () -> VAD
        raise ValueError("VAD not configured")

    # TODO use for all translators
    def translator(self, source_language, target_language):
        # type: (str, str) -> AbstractTranslator
        raise ValueError("AbstractTranslator not configured")

    @property
    def face_detector(self):
        # type: () -> FaceDetector
        raise ValueError("FaceDetector not configured")

    def object_detector(self, target):
        # type: () -> ObjectDetector
        raise ValueError("ObjectDetector not configured")


class SensorWorkerContainer(DIContainer):
    def start_object_detector(self, target):
        # type: (str) -> None
        """
        Start object detection worker.

        Parameters
        ----------
        target : str
            The type of object recognition to use.
        """
        raise ValueError("ObjectDetectorWorker not configured")

    def start_face_detector(self):
        # type: () -> None
        """
        Start face detection worker.
        """
        raise ValueError("FaceDetectorWorker not configured")

    def start_speech_recognition(self):
        # type: () -> None
        """
        Start speech recognition worker.
        """
        raise ValueError("SpeecRecognitionWorkers not configured")

    def stop(self):
        # type: () -> None
        """
        Stop workers started in the application.
        """
        pass


class FaceDetector(object):

    TOPIC = "pepper.framework.sensor.api.face_detector.topic"
    TOPIC_NEW = "pepper.framework.sensor.api.face_detector.topic.new"
    TOPIC_KNOWN = "pepper.framework.sensor.api.face_detector.topic.known"

    FEATURE_DIM = 128

    def represent(self, image):
        # type: (np.ndarray) -> Iterable[(np.ndarray, Bounds)]
        """
        Represent Face in Image as 128-dimensional vector

        Parameters
        ----------
        image: np.ndarray
            Image (possibly containing a human face)

        Returns
        -------
        result: list of (np.ndarray, Bounds)
            List of (representation, bounds)
        """
        raise NotImplementedError()


class ObjectDetector(object):

    TOPIC = "pepper.framework.sensor.api.object_detector.topic"

    def classify(self, image):
        # type: (AbstractImage) -> List[Object]
        """
        Classify Objects in Image

        Parameters
        ----------
        image: AbstractImage
            Image (Containing Objects)

        Returns
        -------
        objects: List[Object]
            Classified Objects
        """
        raise NotImplementedError()


class Voice(object):
    """Voice Object (for Voice Activity Detection: VAD)"""

    def __init__(self, frames=None):
        # type: () -> None
        self._queue = Queue()
        self._frames = frames if frames is not None else []
        self._is_open = True

    @property
    def audio(self):
        # type: () -> np.ndarray
        """
        Get Voice Audio (Concatenated Frames)

        Returns
        -------
        audio: np.ndarray
        """
        return np.concatenate(self._frames)

    def add_frame(self, frame):
        # type: (np.ndarray) -> None
        """
        Add Voice Frame (done by VAD)

        Parameters
        ----------
        frame: np.ndarray
        """
        if not self._is_open:
            raise ValueError("Voice is already closed")

        self._queue.put(frame)
        if frame is not None:
            self._frames.append(frame)
        else:
            self._is_open = False

    @property
    def audio_stream(self):
        if self._is_open:
            return iter(self._queue.get, None)
        else:
            return iter(self._frames, None)


class VAD(object):

    TOPIC = "pepper.framework.sensor.api.vad.topic"

    def on_audio(self, frames, callback):
        # type: (Iterable[np.array]) -> None
        raise NotImplementedError()