from pepper.framework.abstract.component import AbstractComponent


class SubtitlesComponent(AbstractComponent):
    def __init__(self):
        # type: () -> None
        super(SubtitlesComponent, self).__init__()

        self._log.info("Initializing SubtitlesComponent")

    def start(self):
        self.start_subtitles()

        super(SubtitlesComponent, self).start()

    def stop(self):
        super(SubtitlesComponent, self).stop()