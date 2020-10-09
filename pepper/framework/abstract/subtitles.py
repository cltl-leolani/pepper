from pepper.framework.abstract.component import AbstractComponent


class SubtitlesComponent(AbstractComponent):
    def __init__(self):
        # type: () -> None
        super(SubtitlesComponent, self).__init__()

        self._log.info("Initializing SubtitlesComponent")

    def start(self):
        started_events = self.start_subtitles()

        super(SubtitlesComponent, self).start()

        timeout = self.config_manager.get_config("DEFAULT").get_float("dependency_timeout")
        for event in started_events:
            event.wait(timeout=timeout)

    def stop(self):
        super(SubtitlesComponent, self).stop()