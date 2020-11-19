import logging

import numpy as np
from google.cloud import speech, translate_v2
from typing import List, Tuple, Iterable, Union

# TODO extract interfaces to .api
from pepper.framework.infra.config.api import ConfigurationManager

logger = logging.getLogger(__name__)


class UtteranceHypothesis(object):
    """
    Automatic Speech Recognition (ASR) Hypothesis

    Parameters
    ----------
    transcript: str
        Utterance Hypothesis Transcript
    confidence: float
        Utterance Hypothesis Confidence
    """

    def __init__(self, transcript, confidence):
        # type: (str, float) -> None

        self._transcript = transcript
        self._confidence = confidence

    @property
    def transcript(self):
        # type: () -> str
        """
        Automatic Speech Recognition Hypothesis Transcript

        Returns
        -------
        transcript: str
        """
        return self._transcript

    @transcript.setter
    def transcript(self, value):
        # type: (str) -> None
        self._transcript = value

    @property
    def confidence(self):
        # type: () -> float
        """
        Automatic Speech Recognition Hypothesis Confidence

        Returns
        -------
        confidence: float
        """
        return self._confidence

    @confidence.setter
    def confidence(self, value):
        # type: (float) -> None
        self._confidence = value

    def __repr__(self):
        return "<'{}' [{:3.2%}]>".format(self.transcript, self.confidence)


class AbstractTranslator(object):
    """
    Abstract Translator

    Parameters
    ----------
    source: str
        Two Character Source Language Code
    target: str
        Two Character Target Language Code
    """

    def __init__(self, source, target):
        # type: (str, str) -> None
        self._source = source
        self._target = target

    @property
    def source(self):
        # type: () -> str
        """
        Source Language

        Returns
        -------
        source: str
            Two Character Source Language Code
        """
        return self._source

    @property
    def target(self):
        # type: () -> str
        """
        Target Language

        Returns
        -------
        target: str
            Two Character Target Language Code
        """
        return self._target

    def translate(self, text):
        # type: (str) -> str
        """
        Translate Text from Source to Target Language

        Parameters
        ----------
        text: str

        Returns
        -------
        translated_text: str
            Translated Text
        """
        raise NotImplementedError()


class GoogleTranslator(AbstractTranslator):
    """
    Google Translator

    Parameters
    ----------
    source: str
        Two Character Source Language Code
    target: str
        Two Character Target Language Code
    """

    def __init__(self, source, target):
        # type: (str, str) -> None
        super(GoogleTranslator, self).__init__(source, target)

    def translate(self, text):
        # type: (str) -> str
        """
        Translate Text from Source to Target Language

        Parameters
        ----------
        text: str

        Returns
        -------
        translated_text: str
            Translated Text
        """
        if self.source == self.target:
            return text

        client = translate_v2.Client(target_language=self.target)
        translation = client.translate(
            text, source_language=self.source, target_language=self.target)

        return translation['translatedText']


class AbstractASR(object):
    """
    Abstract Automatic Speech Recognition (ASR)

    Parameters
    ----------
    language: str
        Language Code <LC> & Region Code <RC> -> "LC-RC"
    """

    TOPIC = "pepper.framework.sensor.api.asr.topic"

    MAX_ALTERNATIVES = 10

    def __init__(self, language):
        # type: (str) -> None
        self._language = language
        self._log = logger.getChild("{} ({})".format(
            self.__class__.__name__, self.language))

    @property
    def language(self):
        # type: () -> str
        """
        Automatic Speech Recognition Language

        Returns
        -------
        language: str
            Language Code <LC> & Region Code <RC> -> "LC-RC"
        """
        return self._language

    def transcribe(self, audio):
        # type: (np.ndarray) -> List[UtteranceHypothesis]
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray
            Audio Samples (Containing Speech)

        Returns
        -------
        transcript: List[UtteranceHypothesis]
        """
        raise NotImplementedError()


class BaseGoogleASR(AbstractASR, GoogleTranslator):
    """
    Abstract Base Google Automatic Speech Recognition (ASR)

    Handles common parameters for SynchronousGoogleASR and StreamedGoogleASR

    Parameters
    ----------
    language: str
        Language Code <LC> & Region Code <RC> -> "LC-RC"
    sample_rate: int
        Number of Audio Samples per second that will be handled to ASR transcription (16k is nice!)
    hints: Tuple[str]
        Words or Phrases that ASR should be extra sensitive to
    """

    def __init__(self, configuration_manager, language=None, hints=()):
        # type: (ConfigurationManager, str, Iterable[str]) -> None
        config = configuration_manager.get_config(
            "pepper.framework.sensors.asr")
        application_language = language if language else config.get(
            "application_language")
        internal_language = config.get("internal_language")
        sample_rate = config.get_int("microphone_sample_rate")

        AbstractASR.__init__(self, application_language)
        GoogleTranslator.__init__(
            self, application_language[:2], internal_language[:2])

        self._client = speech.SpeechClient()
        self._config = speech.RecognitionConfig(

            # Each Sample is of dtype int16
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,

            # The are 'sample_rate' samples per second
            sample_rate_hertz=sample_rate,

            # The Language & Region
            # Tip: use en-GB for better understanding of 'academic English'
            language_code=application_language,

            # The maximum number of hypotheses to generate per speech recognition
            max_alternatives=self.MAX_ALTERNATIVES,

            # Particular words or phrases the Speech Recognition should be extra sensitive to
            speech_contexts=[speech.SpeechContext(phrases=hints)])

        self._log = logger.getChild(self.__class__.__name__)
        self._log.debug("Booted ({} -> {})".format(self.source, self.target))

    def transcribe(self, audio):
        # type: (np.ndarray) -> List[UtteranceHypothesis]
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray
            Audio Samples (Containing Speech)

        Returns
        -------
        transcript: List[UtteranceHypothesis]
        """
        raise NotImplementedError()


class StreamedGoogleASR(BaseGoogleASR):
    """
    Streamed Google Automatic Speech Recognition (ASR)

    Recognises Speech 'live' as it is spoken. Should be faster than Synchronous ASR

    Parameters
    ----------
    language: str
        Language Code <LC> & Region Code <RC> -> "LC-RC"
    sample_rate: int
        Number of Audio Samples per second that will be handled to ASR transcription (16k is nice!)
    hints: Tuple[str]
        Words or Phrases that ASR should be extra sensitive to
    """

    def __init__(self, configuration_mananger, language=None, hints=()):
        # type: (ConfigurationManager, str, Iterable[str]) -> None
        super(StreamedGoogleASR, self).__init__(
            configuration_mananger, language, hints)

        # String Containing Live Hypothesis -> used for debugging
        # Don't use the contents of this string for any important logic, because:
        #   - Contents change all the time as Utterances progress
        #   - Contents get cleared as soon as a (possible) new Utterance starts
        #   - The actual Hypotheses may differ from the live string due to Google Smarts...
        # Use the transcribe method instead!
        self._live = ""

        self._streaming_config = speech.StreamingRecognitionConfig(

            # The Config from BaseGoogleASR
            config=self._config,

            # Finalize Transcription after a single Utterance! (Keep it True)
            single_utterance=True,

            # Provide 'live' transcription: see self._live docs
            interim_results=True
        )

    @property
    def live(self):
        # type: () -> Union[str, unicode]
        """
        Live Speech Transcript String (Debug/Visual purposes only)

        Returns
        -------
        live: str
            Live Speech Transcript String
        """
        return self._live

    def transcribe(self, audio):
        # type: (Iterable[np.ndarray]) -> List[UtteranceHypothesis]
        """
        Transcribe Speech in Audio (Streamed)

        Instead of a single Block of Audio, this function takes an Iterable of Audio frames.
        One frame is processed at a time while the audio is being generated by the speaker.
        This provides a faster ASR than the synchronous version, and a live representation of the utterance.
        TODO: this breaks the abstract specification, is there a neater way to do this?

        Parameters
        ----------
        audio: Iterable[numpy.ndarray]
            Iterable of Audio Samples (Containing Speech)

        Returns
        -------
        transcript: List[UtteranceHypothesis]
        """

        # TODO: Sometimes this fails! (network issues?) Current Solution: Retry a few times!
        for i in range(3):
            try:
                return self._transcribe(audio)
            except:
                self._log.exception(
                    "ASR Transcription Error (try {})".format(i + 1))

        return []  # Return an empty list if ASR transcription fails

    def _transcribe(self, audio):
        # type: (Iterable[np.ndarray]) -> List[UtteranceHypothesis]
        """
        (Private) Transcribe Speech in Audio (Streamed)

        Instead of a single Block of Audio, this function takes an Iterable of Audio frames.
        One frame is processed at a time while the audio is being generated by the speaker.
        This provides a faster ASR than the synchronous version, and a live representation of the utterance.
        TODO: this breaks the abstsract specification, is there a neater way to do this?

        Parameters
        ----------
        audio: Iterable[numpy.ndarray]
            Iterable of Audio Samples (Containing Speech)

        Returns
        -------
        transcript: List[UtteranceHypothesis]
        """

        hypotheses = []

        # Iterate over API Responses generated by each chunk of speech
        for response in self._client.streaming_recognize(self._streaming_config, self._request(audio)):
            live = ""  # Reset Live Speech
            for result in response.results:
                # If ASR is done processing a whole Utterance
                if result.is_final:
                    for alternative in result.alternatives:
                        # (Possibly translate) Speech transcript
                        transcript = self.translate(alternative.transcript)
                        hypotheses.append(UtteranceHypothesis(
                            transcript, alternative.confidence))

                # If not Final (a.k.a. speech is still going on)
                elif result.alternatives:
                    live += result.alternatives[0].transcript

            # Update current live string (to be accessible through StreamedGoogleASR.live)
            self._live = live

        # When a single utterance is done, return UtteranceHypotheses (sorted by confidence)
        return sorted(hypotheses, key=lambda hypothesis: hypothesis.confidence, reverse=True)

    @staticmethod
    def _request(audio):
        """
        Wrap audio chunks into StreamingRecognizeRequest objects

        Parameters
        ----------
        audio: Iterable[np.ndarray]
        """
        return (speech.StreamingRecognizeRequest(audio_content=frame.tobytes())
                for frame in audio)


class SynchronousGoogleASR(BaseGoogleASR):
    """
    Synchronous Google Automatic Speech Recognition (ASR)

    Recognises Speech 'live' as it is spoken. Should be faster than Synchronous ASR

    Parameters
    ----------
    language: str
        Language Code <LC> & Region Code <RC> -> "LC-RC"
    sample_rate: int
        Number of Audio Samples per second that will be handled to ASR transcription (16k is nice!)
    hints: Tuple[str]
        Words or Phrases that ASR should be extra sensitive to
    """

    def __init__(self, configuration_manager, language=None, hints=()):
        # type: (str, int, Iterable[str]) -> None
        super(SynchronousGoogleASR, self).__init__(
            configuration_manager, language, hints)

    def transcribe(self, audio):
        # type: (np.ndarray) -> List[UtteranceHypothesis]
        """
        Transcribe Speech in Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        hypotheses: List[UtteranceHypothesis]
        """
        hypotheses = []
        for result in self._client.recognize(self._config, self._request(audio)).results:
            for alternative in result.alternatives:
                hypotheses.append(UtteranceHypothesis(self.translate(
                    alternative.transcript), alternative.confidence))
        return sorted(hypotheses, key=lambda hypothesis: hypothesis.confidence, reverse=True)

    @staticmethod
    def _request(audio):
        """
        Wrap Audio in RecognitionAudio

        Parameters
        ----------
        audio: np.ndarray

        Returns
        -------
        request: speech.RecognitionAudio
        """
        return speech.RecognitionAudio(content=audio.tobytes())
