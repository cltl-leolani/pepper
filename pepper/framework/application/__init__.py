"""
Abstract
========

The framework.application package contains specifications for:

- Applications: :class:`~pepper.framework.application.application.AbstractApplication`
- Components & Intentions: :class:`~pepper.framework.application.component.AbstractComponent` :class:`~pepper.framework.application.intention.AbstractIntention`

The :class:`~pepper.framework.application.application.AbstractApplication` class forms the base of each application.

Applications can be extended by adding one or more :class:`~pepper.framework.application.component.AbstractComponent`.
More complex Applications can be build on several instances of
:class:`~pepper.framework.application.intention.AbstractIntention`, each of which deals with one task within an app.
"""