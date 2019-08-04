"""Middleware contains the actual communication logic for talking to wysteria.


Files
-----

abstract_middleware.py
    An abstract class contract that a subclass must implement in order to be used as a viable
    middleware.

impl_nats.py
    A Nats.io implementation of the abstract middleware class.

impl_grpc.py
    A gRPC implementation of the the middleware class

wgrpc/
    Auto generated files for gRPC by protobuf.


Exported
--------

  NatsMiddleware
    A Nats.io implementation of the abstract middleware class

  GRPCMiddleware
    A gRPC implementation of the the middleware class



"""

from wysteria.middleware.impl_nats import NatsMiddleware
from wysteria.middleware.impl_grpc import GRPCMiddleware


__all__ = [
    "NatsMiddleware",
    "GRPCMiddleware",
]
