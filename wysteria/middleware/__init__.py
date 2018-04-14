"""Middleware contains the actual communication logic for talking to wysteria.


Files
-----

abstract_middleware.py
    An abstract class contract that a subclass must implement in order to be used as a viable
    middleware.

impl_nats.py
    A Nats.io implementation of the abstract middleware class.


Exported
--------

  NatsMiddleware
    A Nats.io implementation of the abstract middleware class


"""

from wysteria.middleware.impl_nats import WysteriaNatsMiddleware as NatsMiddleware


__all__ = [
    "NatsMiddleware",
]
