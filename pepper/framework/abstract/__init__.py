"""
Abstract
========

The framework.abstract package contains specifications for:

- Applications: :class:`~pepper.framework.abstract.application.AbstractApplication`
- Components & Intentions: :class:`~pepper.framework.abstract.component.AbstractComponent` :class:`~pepper.framework.abstract.intention.AbstractIntention`

The :class:`~pepper.framework.abstract.application.AbstractApplication` class forms the base of each application.

Applications can be extended by adding one or more :class:`~pepper.framework.abstract.component.AbstractComponent`.
More complex Applications can be build on several instances of
:class:`~pepper.framework.abstract.intention.AbstractIntention`, each of which deals with one task within an app.
"""