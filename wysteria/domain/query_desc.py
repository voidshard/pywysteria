"""

"""
from wysteria.domain.base import WysBaseObj


class QueryDesc(WysBaseObj):
    """
    QueryDesc represents a single query param to a Wysteria server
    """
    def __init__(self):
        self._id = ""
        self._parent = ""
        self._versionnumber = 0
        self._itemtype = ""
        self._variant = ""
        self._facets = {}
        self._name = ""
        self._resourcetype = ""
        self._location = ""
        self._linkdst = ""
        self._linksrc = ""

    @property
    def is_valid(self):
        """Return if at least one of our search params is set.

        ToDo: Consider not allowing resource_type / name queries without
        a parent or id set.

        Returns:
            bool
        """
        return any([
            self._id,
            self._parent,
            self._versionnumber,
            self._itemtype,
            self._variant,
            self._facets,
            self._name,
            self._resourcetype,
            self._location,
            self._linksrc,
            self._linkdst
        ])

    def id(self, val):
        self._id = val
        return self

    def parent(self, val):
        self._parent = val
        return self

    def version_number(self, val):
        self._versionnumber = val
        return self

    def item_type(self, val):
        self._itemtype = val
        return self

    def item_variant(self, val):
        self._variant = val
        return self

    def has_facets(self, val):
        self._facets = val
        return self

    def name(self, val):
        self._name = val
        return self

    def resource_type(self, val):
        self._resourcetype = val
        return self

    def resource_location(self, val):
        self._location = val
        return self

    def link_destination(self, val):
        self._linkdst = val
        return self

    def link_source(self, val):
        self._linksrc = val
        return self

    def __repr__(self):
        return "<%s>" % self.__class__.__name__
