"""
Component
=========

Applications are made out of several instances of :class:`~pepper.framework.abstract.component.AbstractComponent`,
which expose various methods and events to applications. They're summarized below:

- :class:`~pepper.framework.component.speech_recognition.SpeechRecognitionComponent` exposes the :meth:`~pepper.framework.component.speech_recognition.SpeechRecognitionComponent.on_transcript` event.
- :class:`~pepper.framework.component.brain.BrainComponent` exposes :class:`pepper.brain.long_term_memory.LongTermMemory` to the application.

Some Components are more complex and require other components to work. They will raise a :class:`pepper.framework.abstract.component.ComponentDependencyError` if dependencies are not met.

- :class:`~pepper.framework.component.context.ContextComponent` exposes :class:`pepper.framework.context.Context` to the application and overrides the :meth:`~pepper.framework.component.context.ContextComponent.say` method to work with the :class:`~pepper.language.language.Chat` class. It also exposes the :meth:`~pepper.framework.component.context.ContextComponent.on_chat_turn`, :meth:`~pepper.framework.component.context.ContextComponent.on_chat_enter` & :meth:`~pepper.framework.component.context.ContextComponent.on_chat_exit` events.
- :class:`~pepper.framework.component.statistics.StatisticsComponent` displays realtime system statistics in the command line.
- :class:`~pepper.framework.component.scene.SceneComponent` creates a 3D scatterplot of the visible space.
- :class:`~pepper.framework.component.display.display.DisplayComponent` shows the live camera feedback and the 3D view of the current space, including the objects that are observed.
"""

from .scene import SceneComponent
from .statistics import StatisticsComponent
from .display.display import DisplayComponent
