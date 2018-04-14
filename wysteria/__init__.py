"""The wysteria module provides a python interface for talking to a wysteria asset management
server.


Files:
------

- client.py
    high level class that wraps a middleware connection & adds some helpful functions.
- constants.py
    various constants used
- errors.py
    contains various exceptions that can be raised
- search.py
    simple class for building wysteria search params
- utils.py
    simple utility functions for reading config files and other misc stuff


Modules
-------

 - domain
    python wrappers around various wysteria native objects
 - middleware
    python implementations of the communication protocol for talking to the server


Exported
--------

  Client
    Wysteria client wrapper class

  TlsConfig
    Simplified TLS config object that can be used to secure the middleware connection

  errors
    Error module that contains various exceptions that can be raised by the client

  default_client
    Sugar function to build & configure a client. Searches for a wysteria client config & falls
    back on using some default hardcoded settings if all else fails.

  from_config
    Construct & configure a client from a given config file.

"""
from wysteria.client import Client
from wysteria import errors
from wysteria.constants import FACET_COLLECTION
from wysteria.constants import FACET_ITEM_TYPE
from wysteria.constants import FACET_ITEM_VARIANT
from wysteria.constants import FACET_LINK_TYPE
from wysteria.constants import VALUE_LINK_TYPE_VERSION
from wysteria.constants import VALUE_LINK_TYPE_ITEM
from wysteria.utils import default_client
from wysteria.utils import from_config


__all__ = [
    "Client",
    "errors",
    "default_client",
    "from_config",
    "FACET_COLLECTION",
    "FACET_ITEM_TYPE",
    "FACET_ITEM_VARIANT",
    "FACET_LINK_TYPE",
    "VALUE_LINK_TYPE_VERSION",
    "VALUE_LINK_TYPE_ITEM",
]
