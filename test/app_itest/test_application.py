import logging
import sys
import unittest

import importlib_resources
import mock
import numpy as np

from pepper import CameraResolution, config
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.abstract.face_detection import FaceRecognitionComponent
from pepper.framework.abstract.object_detection import ObjectDetectionComponent
from pepper.framework.abstract.speech_recognition import SpeechRecognitionComponent
from pepper.framework.backend.abstract.backend import AbstractBackend
from pepper.framework.backend.abstract.camera import AbstractCamera, AbstractImage
from pepper.framework.backend.abstract.camera import TOPIC as CAM_TOPIC
from pepper.framework.backend.abstract.led import AbstractLed
from pepper.framework.backend.abstract.microphone import AbstractMicrophone
from pepper.framework.backend.abstract.microphone import TOPIC as MIC_TOPIC
from pepper.framework.backend.abstract.motion import AbstractMotion
from pepper.framework.backend.abstract.tablet import AbstractTablet
from pepper.framework.backend.abstract.text_to_speech import AbstractTextToSpeech
from pepper.framework.backend.container import BackendContainer
from pepper.framework.config.local import LocalConfigurationContainer
from pepper.framework.context.container import DefaultContextWorkerContainer, DefaultContextContainer
from pepper.framework.di_container import singleton
from pepper.framework.event.api import EventBusContainer
from pepper.framework.event.memory import SynchronousEventBusContainer
from pepper.framework.resource.threaded import ThreadedResourceContainer
from pepper.framework.sensor.api import FaceDetector, ObjectDetector, AbstractTranslator, AbstractASR, Object, \
    UtteranceHypothesis, SensorContainer, VAD, Voice
from pepper.framework.sensor.container import DefaultSensorWorkerContainer
from pepper.framework.util import Bounds
from test import util

logger = logging.getLogger("pepper")
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel(logging.ERROR)

TEST_IMG = np.zeros((128,))
TEST_BOUNDS = Bounds(0.0, 0.0, 1.0, 1.0)


class TestBackendContainer(BackendContainer, EventBusContainer):
    @property
    @singleton
    def backend(self):
        return TestBackend(self.event_bus, self.resource_manager)


class TestBackend(AbstractBackend):
    def __init__(self, event_bus, resource_manager):
        super(TestBackend, self).__init__(camera=AbstractCamera(CameraResolution.VGA, 1, event_bus, resource_manager),
                                          microphone=AbstractMicrophone(8000, 1, event_bus, resource_manager),
                                          text_to_speech=AbstractTextToSpeech("nl", event_bus, resource_manager),
                                          motion=AbstractMotion(event_bus),
                                          led=AbstractLed(event_bus),
                                          tablet=AbstractTablet(event_bus))


class TestSensorContainer(SensorContainer):
    @property
    @singleton
    def vad(self):
        mock_vad = mock.create_autospec(VAD)
        mock_vad.on_audio.side_effect = lambda audio, callback: callback(Voice(np.zeros((80,1), dtype=np.int16)))

        return mock_vad

    def asr(self, language="nl"):
        def asr_fct(voice):
            return [UtteranceHypothesis("Test one two", 1.0)]

        mock_asr = mock.create_autospec(AbstractASR)
        mock_asr.transcribe.side_effect = asr_fct

        return mock_asr

    def translator(self, source_language, target_language):
        mock_translator = mock.create_autospec(AbstractTranslator)
        mock_translator.translate.side_effect = lambda text: "Translated: " + text

        return mock_translator

    @property
    def face_detector(self):
        mock_face_detector = mock.create_autospec(FaceDetector)
        mock_face_detector.represent.return_value = [(TEST_IMG, TEST_BOUNDS)]

        return mock_face_detector

    def object_detector(self, target):
        mock_object_detector = mock.create_autospec(ObjectDetector)
        mock_object_detector.classify.side_effect = lambda image: [Object("test_object", 1.0, TEST_BOUNDS, image)]
        mock_object_detector.target = target

        return mock_object_detector


class ApplicationContainer(TestBackendContainer,
                           DefaultContextWorkerContainer,
                           DefaultContextContainer,
                           DefaultSensorWorkerContainer,
                           TestSensorContainer,
                           SynchronousEventBusContainer,
                           ThreadedResourceContainer,
                           LocalConfigurationContainer):
    pass


class TestApplication(ApplicationContainer, AbstractApplication,
                      SpeechRecognitionComponent,
                      FaceRecognitionComponent,
                      ObjectDetectionComponent):
    def __init__(self):
        super(TestApplication, self).__init__()
        self.objects = []
        self.faces = []
        self.faces_new = []
        self.faces_known = []
        self.hypotheses = []

    def on_object(self, objects):
        self.objects.extend(objects)

    def on_face(self, faces):
        self.faces.extend(faces)

    def on_face_new(self, faces):
        # type: (List[Face]) -> None
        self.faces_new.extend(faces)

    def on_face_known(self, faces):
        # type: (List[Face]) -> None
        self.faces_known.extend(faces)

    def on_transcript(self, hypotheses, audio):
        self.hypotheses.extend(hypotheses)


class ApplicationITest(unittest.TestCase):
    def setUp(self):
        with importlib_resources.path(__package__, "test.config") as test_config:
            LocalConfigurationContainer.load_configuration(str(test_config), [])
        self.application = TestApplication()

    def tearDown(self):
        self.application.stop()
        del self.application

    def test_mic_events(self):
        mic_events = []
        def handle_audio_event(event):
            mic_events.append(event)

        self.application.event_bus.subscribe(MIC_TOPIC, handle_audio_event)
        self.application.start()

        mic = self.application.backend.microphone
        audio_frame = np.random.rand(80).astype(np.int16)
        mic.on_audio(audio_frame)

        util.await(lambda: len(mic_events) > 0, msg="mic event")

        self.assertEqual(len(mic_events), 1)
        np.testing.assert_array_equal(mic_events[0].payload, audio_frame)

        try:
            util.await(lambda: len(mic_events) > 1, max=5)
        except unittest.TestCase.failureException:
            # Expect no more audio events
            pass

    def test_camera_events(self):
        image_events = []

        def handle_image_event(event):
            image_events.append(event)

        self.application.event_bus.subscribe(CAM_TOPIC, handle_image_event)
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)

        cam = self.application.backend.camera
        cam.on_image(image)

        util.await(lambda: len(image_events) > 0, msg="images")

        self.assertEqual(len(image_events), 1)
        np.testing.assert_array_equal(image_events[0].payload, image)

        try:
            util.await(lambda: len(image_events) > 1, max=5)
        except unittest.TestCase.failureException:
            # Expect no more audio events
            pass

    def test_object_events(self):
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)

        cam = self.application.backend.camera
        cam.on_image(image)

        util.await(lambda: len(self.application.objects) > 1, msg="objects")

        self.assertEqual(2, len(self.application.objects))
        self.assertListEqual(2*["test_object"], [obj.name for obj in self.application.objects])

    def test_face_events(self):
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)

        cam = self.application.backend.camera
        cam.on_image(image)

        util.await(lambda: len(self.application.faces) > 0, msg="faces")

        self.assertEqual(1, len(self.application.faces))
        self.assertEqual(config.HUMAN_UNKNOWN, self.application.faces[0].name)

    def test_face_new_events(self):
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)

        cam = self.application.backend.camera
        cam.on_image(image)

        util.await(lambda: len(self.application.faces_new) > 0, msg="faces")

        self.assertEqual(1, len(self.application.faces_new))
        self.assertEqual(config.HUMAN_UNKNOWN, self.application.faces_new[0].name)

    def test_face_known_events(self):
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)

        cam = self.application.backend.camera
        cam.on_image(image)

        try:
            util.await(lambda: len(self.application.faces_known) > 0, max=5, msg="faces")
            raise unittest.TestCase.failureException("Unexpected faces: " + str(self.application.faces_known))
        except:
            pass

    def test_speech_events(self):
        self.application.start()

        mic = self.application.backend.microphone
        audio_frame = np.random.rand(80).astype(np.int16)
        mic.on_audio(audio_frame)

        util.await(lambda: len(self.application.hypotheses) > 0, msg="mic event")

        self.assertEqual(1, len(self.application.hypotheses))
        self.assertEqual("Test one two", self.application.hypotheses[0].transcript)

    def test_context_on_chat_enter(self):
        self.application.start()

        mic = self.application.backend.microphone
        audio_frame = np.random.rand(80).astype(np.int16)
        mic.on_audio(audio_frame)

        util.await(lambda: len(self.application.hypotheses) > 0, msg="mic event")

        self.assertEqual(1, len(self.application.hypotheses))
        self.assertEqual("Test one two", self.application.hypotheses[0].transcript)


if __name__ == '__main__':
    unittest.main()