from pepper.framework import *
from pepper import logger

from pepper.language import Utterance
from pepper.language.generation.thoughts_phrasing import phrase_thoughts
from pepper.language.generation.reply import reply_to_question

from .responder import Responder, ResponderType
from pepper.language import UtteranceType

from pepper.knowledge import sentences, animations
from random import choice

import re

from typing import Optional, Union, Tuple, Callable


class BrainResponder(Responder):
    def __init__(self):
        self._log = logger.getChild(self.__class__.__name__)

    @property
    def type(self):
        return ResponderType.Brain

    @property
    def requirements(self):
        return [TextToSpeechComponent, BrainComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent, BrainComponent]) -> Optional[Tuple[float, Callable]]

        try:
            utterance.analyze()

            self._log.debug("TRIPLE: {}".format(utterance.triple))

            if utterance.triple is not None:
                if utterance.type == UtteranceType.QUESTION:
                    brain_response = app.brain.query_brain(utterance)
                    reply = reply_to_question(brain_response)
                else:
                    brain_response = app.brain.update(utterance, reason_types=True)  # Searches for types in dbpedia
                    reply = phrase_thoughts(brain_response, True, True)

                self._log.debug("REPLY: {}".format(reply))

                if (isinstance(reply, str) or isinstance(reply, unicode)) and reply != "":
                    # Return Score and Response
                    # Make sure to not execute the response here, but just to return the response function
                    return 1.0, lambda: app.say(re.sub(r"[\s+_]", " ", reply))
                elif brain_response:
                    # Thank Human for the Data!
                    return 1.0, lambda: app.say("{} {}".format(choice([
                        choice(sentences.THANK), choice(sentences.HAPPY)
                    ]), choice(sentences.PARSED_KNOWLEDGE)), animations.HAPPY)

        except Exception as e:
            self._log.error(e)
