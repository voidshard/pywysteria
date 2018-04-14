"""Domain module contains python classes used throughout the repo.


Files
-----

base.py
    Contains abstract / parent classes that are used within the module

collection.py
    Contains Collection class

item.py
    Contains Item class

version.py
    Contains Version class

link.py
    Contains Link class

resource.py
    Contains Resource class

query_desc.py
    Contains QueryDesc class. This is used by the Search class but isn't intended to be directly
    exposed.


Exported
--------

As you might expect, this exposes only the domain object classes:
    - Collection
    - Item
    - Version
    - Resource
    - Link
    - QueryDesc

"""

from wysteria.domain.collection import Collection
from wysteria.domain.item import Item
from wysteria.domain.version import Version
from wysteria.domain.resource import Resource
from wysteria.domain.link import Link
from wysteria.domain.query_desc import QueryDesc


__all__ = [
    "Collection",
    "Item",
    "Version",
    "Resource",
    "Link",
    "QueryDesc",
]
