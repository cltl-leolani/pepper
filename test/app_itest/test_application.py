import logging
import sys
import threading
import unittest
from time import sleep

import importlib_resources
import mock
import numpy as np

from pepper import CameraResolution, config
from pepper.framework.application.application import AbstractApplication
from pepper.framework.application.context import ContextComponent
from pepper.framework.application.face_detection import FaceRecognitionComponent
from pepper.framework.application.intention import AbstractIntention
from pepper.framework.application.object_detection import ObjectDetectionComponent
from pepper.framework.application.speech_recognition import SpeechRecognitionComponent
from pepper.framework.application.text_to_speech import TextToSpeechComponent
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
from pepper.framework.infra.config.local import LocalConfigurationContainer
from pepper.framework.context.container import DefaultContextWorkerContainer, DefaultContextContainer
from pepper.framework.infra.di_container import singleton, DIContainer
from pepper.framework.infra.event.api import EventBusContainer
from pepper.framework.infra.event.memory import SynchronousEventBusContainer
from pepper.framework.infra.resource.threaded import ThreadedResourceContainer
from pepper.framework.sensor.api import FaceDetector, ObjectDetector, AbstractTranslator, AbstractASR, Object, \
    UtteranceHypothesis, SensorContainer, VAD, Voice
from pepper.framework.sensor.container import DefaultSensorWorkerContainer
from pepper.framework.infra.util import Bounds
from test import util

# logger = logging.getLogger("pepper")
# handler = logging.StreamHandler(stream=sys.stdout)
# handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
#                                        datefmt='%Y-%m-%d %H:%M:%S'))
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)

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
                                          motion=AbstractMotion(event_bus, resource_manager),
                                          led=AbstractLed(event_bus, resource_manager),
                                          tablet=AbstractTablet(event_bus, resource_manager))


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
        mock_object_detector.classify.side_effect = lambda image: [Object("person", 1.0, TEST_BOUNDS, image)]
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


class TestIntention(ApplicationContainer, AbstractIntention,
                      TextToSpeechComponent,
                      SpeechRecognitionComponent,
                      FaceRecognitionComponent,
                      ObjectDetectionComponent,
                      ContextComponent):
    def __init__(self):
        super(TestIntention, self).__init__()
        self.objects = []
        self.faces = []
        self.faces_new = []
        self.faces_known = []
        self.hypotheses = []
        self.chat_entries = []
        self.chat_turns = []
        self.chat_exits = 0

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

    def on_chat_enter(self, person):
        # type: (str) -> None
        self.chat_entries.append(person)
        self.context.start_chat(person)

    def on_chat_turn(self, utterance):
        # type: (Utterance) -> None
        self.chat_turns.append(utterance)
        self.context.stop_chat()

    def on_chat_exit(self):
        # type: () -> None
        self.chat_exits += 1


class TestApplication(AbstractApplication, ApplicationContainer):
    def __init__(self, intention):
        super(TestApplication, self).__init__(intention)


class ApplicationITest(unittest.TestCase):
    def setUp(self):
        with importlib_resources.path(__package__, "test.config") as test_config:
            LocalConfigurationContainer.load_configuration(str(test_config), [])
        self.intention = TestIntention()
        self.application = TestApplication(self.intention)

    def tearDown(self):
        self.application.stop()
        del self.application
        DIContainer._singletons.clear()

        # Try to ensure that the application is stopped
        try:
            util.await(lambda: threading.active_count() < 2, max=100)
        except:
            sleep(1)

    def test_mic_events(self):
        mic_events = []
        def handle_audio_event(event):
            mic_events.append(event)

        self.intention.event_bus.subscribe(MIC_TOPIC, handle_audio_event)
        self.application.start()

        mic = self.intention.backend.microphone
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

        self.intention.event_bus.subscribe(CAM_TOPIC, handle_image_event)
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)

        cam = self.intention.backend.camera
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

        cam = self.intention.backend.camera
        cam.on_image(image)

        util.await(lambda: len(self.intention.objects) > 1, msg="objects")

        self.assertEqual(2, len(self.intention.objects))
        self.assertListEqual(2 * ["person"], [obj.name for obj in self.intention.objects])

    def test_face_events(self):
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)

        cam = self.intention.backend.camera
        cam.on_image(image)

        util.await(lambda: len(self.intention.faces) > 0, msg="faces")

        self.assertEqual(1, len(self.intention.faces))
        self.assertEqual(config.HUMAN_UNKNOWN, self.intention.faces[0].name)

    def test_face_new_events(self):
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)

        cam = self.intention.backend.camera
        cam.on_image(image)

        util.await(lambda: len(self.intention.faces_new) > 0, msg="faces")

        self.assertEqual(1, len(self.intention.faces_new))
        self.assertEqual(config.HUMAN_UNKNOWN, self.intention.faces_new[0].name)

    def test_face_known_events(self):
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)

        cam = self.intention.backend.camera
        cam.on_image(image)

        try:
            util.await(lambda: len(self.intention.faces_known) > 0, max=5, msg="faces")
            raise unittest.TestCase.failureException("Unexpected faces: " + str(self.intention.faces_known))
        except:
            pass

    def test_speech_events(self):
        self.application.start()

        mic = self.intention.backend.microphone
        audio_frame = np.random.rand(80).astype(np.int16)
        mic.on_audio(audio_frame)

        util.await(lambda: len(self.intention.hypotheses) > 0, msg="hypotheses")

        self.assertEqual(1, len(self.intention.hypotheses))
        self.assertEqual("Test one two", self.intention.hypotheses[0].transcript)

    def test_context_on_chat_enter(self):
        self.application.start()

        bounds = Bounds(0.0, 0.0, 1.0, 1.0)
        image = AbstractImage(np.zeros((2, 2, 3)), bounds)
        cam = self.intention.backend.camera
        cam.on_image(image)

        util.await(lambda: len(self.intention.chat_entries) > 0, msg="chat_enter", max=1000)

        self.assertEqual(1, len(self.intention.chat_entries))
        self.assertEqual(config.HUMAN_UNKNOWN, self.intention.chat_entries[0])

        mic = self.intention.backend.microphone
        audio_frame = np.random.rand(80).astype(np.int16)
        mic.on_audio(audio_frame)

        util.await(lambda: len(self.intention.chat_turns) > 0, msg="chat_turn", max=2000)

        self.assertEqual(1, len(self.intention.chat_turns))
        self.assertEqual("Test one two", self.intention.chat_turns[0].transcript)
        self.assertEqual(config.HUMAN_UNKNOWN, self.intention.chat_turns[0].chat_speaker)

        util.await(lambda: self.intention.chat_exits > 0, msg="chat_exit", max=1000)

        self.assertEqual(1, self.intention.chat_exits)


if __name__ == '__main__':
    unittest.main()