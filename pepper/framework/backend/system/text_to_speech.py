

import os
import tempfile
import wave

import pyaudio
from google.cloud import texttospeech
from typing import Union, Optional

from pepper.framework.backend.abstract.text_to_speech import AbstractTextToSpeech
from pepper.framework.infra.event.api import EventBus
from pepper.framework.infra.resource.api import ResourceManager
from pepper.framework.sensor.asr import AbstractTranslator


_AUDIO_FILE_BUFFER_SIZE = 1024


class SystemTextToSpeech(AbstractTextToSpeech):
    """
    System Text to Speech

    Parameters
    ----------
    language: str
        `Language Code <https://cloud.google.com/speech/docs/languages>`_
    """
    GENDER = 2  # "Female" or 1 "Male"
    TYPE = "Standard"

    def __init__(self, translator, language, event_bus, resource_manager):
        # type: (AbstractTranslator, str, EventBus, ResourceManager) -> None
        AbstractTextToSpeech.__init__(self, language, event_bus, resource_manager)
        self._translator = translator

        self._client = texttospeech.TextToSpeechClient()
        self._voice = texttospeech.VoiceSelectionParams(language_code=language, ssml_gender=self.GENDER)

        # Select the type of audio file you want returned
        self._audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

        self._log.debug("Booted ({} -> {})".format(self._translator.source, self._translator.target))

    def on_text_to_speech(self, text, animation=None):
        # type: (Union[str, unicode], Optional[str]) -> None
        """
        Say something through Text to Speech

        Parameters
        ----------
        text: str
        animation: str
        """

        for i in range(3):
            try:
                synthesis_input = texttospeech.SynthesisInput(text=self._translator.translate(text))
                response = self._client.synthesize_speech(input=synthesis_input, voice=self._voice, audio_config=self._audio_config)
                self._play_sound(response.audio_content)
                return
            except:
                self._log.exception("Couldn't Synthesize Speech ({})".format(i+1))

    def _play_sound(self, mp3):
        tmp_file = None
        try:
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            with tmp_file:
                tmp_file.write(mp3)

            self._play_file(tmp_file.name)
        except:
            self._log.exception("Failed to write temporary file")
        finally:
            if tmp_file and os.path.exists(tmp_file.name):
                # TODO: Sometimes we need to save all data from an experiment. Comment the line below and pass
                os.remove(tmp_file.name)

    def _play_file(self, file):
        with wave.open(file, 'rb') as wav_file:
            width = wav_file.getsampwidth()
            channels = wav_file.getnchannels()
            rate = wav_file.getframerate()
            pa = pyaudio.PyAudio()
            pa_stream = pa.open(
                format=pyaudio.get_format_from_width(width),
                channels=channels,
                rate=rate,
                output=True)

            data = wav_file.readframes(_AUDIO_FILE_BUFFER_SIZE)

            # play stream (looping from beginning of file to the end)
            while data != b'' and data != '':
                # writing to the stream is what *actually* plays the sound.
                pa_stream.write(data)
                data = wav_file.readframes(_AUDIO_FILE_BUFFER_SIZE)

            # cleanup stuff.
            pa_stream.close()
            pa.terminate()
