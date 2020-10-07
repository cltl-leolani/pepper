from pepper.framework.backend.abstract.text_to_speech import TOPIC as TTS_TOPIC
from pepper.framework.event.api import Event
from pepper.framework.multiprocessing import TopicWorker, RejectionStrategy
from pepper.framework.sensor.api import UtteranceHypothesis


class ContextUtteranceWorker(TopicWorker):
    def __init__(self, context, name, event_bus, resource_manager):
        # type: (Context, str, EventBus, ResourceManager) -> None
        super(ContextUtteranceWorker, self).__init__(TTS_TOPIC, event_bus, interval=0, name=name,
                                                     buffer_size=16, rejection_strategy=RejectionStrategy.BLOCK,
                                                     resource_manager=resource_manager,
                                                     requires=[TTS_TOPIC], provides=[])
        self.context = context

    def process(self, event):
        # type: (Event) -> None
        """
        Add utterance to context.

        Parameters
        ----------
        event : Event
        """
        text = event.payload['text']

        if self.context.chatting:
            self.context.chat.add_utterance([UtteranceHypothesis(text, 1.0)], me=True)
