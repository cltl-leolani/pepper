"""Example Application that answers questions posed in natural language using Wikipedia"""

from pepper.app_container import ApplicationContainer
from pepper.framework.abstract.application import AbstractApplication
from pepper.framework.abstract.statistics import StatisticsComponent
from pepper.framework.abstract.text_to_speech import TextToSpeechComponent
from pepper.framework.abstract.speech_recognition import SpeechRecognitionComponent
from pepper.knowledge import Wikipedia  # Class to Query Wikipedia using Natural Language


class WikipediaApplication(ApplicationContainer,
                           AbstractApplication,         # Every Application Inherits from AbstractApplication
                           StatisticsComponent,         # Displays Performance Statistics in Terminal
                           SpeechRecognitionComponent,  # Enables Speech Recognition and the self.on_transcript event
                           TextToSpeechComponent):      # Enables Text to Speech and the self.say method

    def on_transcript(self, hypotheses, audio):
        """
        On Transcript Event.
        Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        hypotheses: List[ASRHypothesis]
            Hypotheses about the corresponding utterance
        audio: numpy.ndarray
            Utterance audio
        """

        # Choose first ASRHypothesis and interpret as question
        question = hypotheses[0].transcript

        # Query Wikipedia with question to (potentially) obtain an answer
        result = Wikipedia.query(question)

        if result:

            # Obtain answer and Thumbnail Image URL from Wikipedia
            answer, url = result
            
            # Limit Answer to a single sentence
            answer = answer.split('.')[0]

            # Tell Answer to Human
            self.say(answer)

        else:

            # Tell Human you don't know
            self.say("I don't know!")


if __name__ == "__main__":
    application = WikipediaApplication()
    application.run()
