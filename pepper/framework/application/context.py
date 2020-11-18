from pepper.framework.application._util import event_payload_handler
from pepper.framework.application.component import AbstractComponent
from pepper.framework.context.api import TOPIC_ON_CHAT_ENTER, TOPIC_ON_CHAT_TURN, TOPIC_ON_CHAT_EXIT
from pepper.language import Utterance


class ContextComponent(AbstractComponent):
    def __init__(self):
        # type: () -> None
        super(ContextComponent, self).__init__()

        self._log.debug("Initializing ContextComponent")

    def start(self):
        self.event_bus.subscribe(TOPIC_ON_CHAT_ENTER, self.__on_chat_enter_handler)
        self.event_bus.subscribe(TOPIC_ON_CHAT_TURN, self.__on_chat_turn_handler)
        self.event_bus.subscribe(TOPIC_ON_CHAT_EXIT, self.__on_chat_exit_handler)
        started_events = self.start_context_worker()

        super(ContextComponent, self).start()

        timeout = self.config_manager.get_config("DEFAULT").get_float("dependency_timeout")
        for event in started_events:
            event.wait(timeout=timeout)

    def stop(self):
        try:
            self.event_bus.unsubscribe(TOPIC_ON_CHAT_ENTER, self.__on_chat_enter_handler)
            self.event_bus.unsubscribe(TOPIC_ON_CHAT_TURN, self.__on_chat_turn_handler)
            self.event_bus.unsubscribe(TOPIC_ON_CHAT_EXIT, self.__on_chat_exit_handler)
        finally:
            super(ContextComponent, self).stop()

    @event_payload_handler
    def __on_chat_enter_handler(self, name):
        self.on_chat_enter(name)

    @event_payload_handler
    def __on_chat_turn_handler(self, utterance):
        self.on_chat_turn(utterance)

    def __on_chat_exit_handler(self, _):
        self.on_chat_exit()

    def on_chat_turn(self, utterance):
        # type: (Utterance) -> None
        """
        On Chat Turn Callback, called every time the speaker utters some Utterance
        Parameters
        ----------
        utterance: Utterance
            Utterance speaker uttered
        """
        pass

    def on_chat_enter(self, person):
        # type: (str) -> None
        """
        On Chat Enter Event. Called every time the conversation logic decides a conversation should start.
        When called, this does not actually automatically start a conversation, this is up to the user to decide.
        Conversations can be started anytime by calling ContextComponent.context.start_chat().
        Parameters
        ----------
        person: str
            The person (or group of people: config.HUMAN_CROWD), the conversation should start with.
        """
        pass

    def on_chat_exit(self):
        # type: () -> None
        """
        On Chat Exit Event. Called every time the conversation logic decides a conversation should stop.
        When called, this does not actually automatically stop a conversation, this is up to the user to decide.
        Conversations can be stopped anytime by calling ContextComponent.context.stop_chat().
        """
        pass