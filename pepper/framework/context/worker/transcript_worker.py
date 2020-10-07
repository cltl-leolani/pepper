import numpy as np
from typing import List

from pepper.framework.context.api import TOPIC_ON_CHAT_TURN
from pepper.framework.event.api import Event
from pepper.framework.multiprocessing import TopicWorker, RejectionStrategy
from pepper.framework.sensor.api import UtteranceHypothesis, AbstractASR


class ContextTranscriptWorker(TopicWorker):
    def __init__(self, context, name, event_bus, resource_manager):
        # type: (Context, str, EventBus, ResourceManager) -> None
        super(ContextTranscriptWorker, self).__init__(AbstractASR.TOPIC, event_bus, interval=0, name=name,
                                                      buffer_size=16, rejection_strategy=RejectionStrategy.BLOCK,
                                                      resource_manager=resource_manager,
                                                      requires=[AbstractASR.TOPIC], provides=[TOPIC_ON_CHAT_TURN])

    def process(self, event):
        # type: (List[UtteranceHypothesis], np.ndarray) -> None
        """
        Add Transcript to Chat (if a current Chat exists)

        Parameters
        ----------
        hypotheses: List[UtteranceHypothesis]
        audio: np.ndarray
        """
        hypotheses = event.payload['hypotheses']

        # TODO
        # with context_lock:
        if self.context.chatting and hypotheses:
            utterance = self.context.chat.add_utterance(hypotheses, False)

            self.event_bus.publish(TOPIC_ON_CHAT_TURN, Event(utterance, None))
