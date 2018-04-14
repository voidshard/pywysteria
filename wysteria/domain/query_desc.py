"""

"""
import copy


class QueryDesc:
    """
    QueryDesc ("Query Description") represents a single query param sent to a wysteria server.

    - An object must match all of the set params in order to be considered a match.
    - Multiple QueryDesc sent to Wysteria will return results that match any of the individual
      QueryDesc objects.
    - A single search request with a list of QueryDesc is sent looking for objects of a given
      type. If the desired object type lacks a property for which a QueryDesc asks for, that
      field is ignored for the purpose of the search.
      That is, if you searched for all collections and matched on {some params} which included
      "ResourceLocation", the "ResourceLocation" requirement will be ignored as Collections do not
      possess this property.

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
    def is_valid(self) -> bool:
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

    def encode(self) -> dict:
        """Return dict representation of this object.

        Returns:
            dict
        """
        return {
            "id": self._id,
            "parent": self._parent,
            "versionnumber": self._versionnumber,
            "itemtype": self._itemtype,
            "variant": self._variant,
            "facets": copy.copy(self._facets),
            "name": self._name,
            "resourcetype": self._resourcetype,
            "location": self._location,
            "linksrc": self._linksrc,
            "linkdst": self._linkdst,
        }

    def id(self, val: str):
        """Match on object by it's Id.

        Args:
            val: an Id to match on

        Returns:
            self
        """
        self._id = val
        return self

    def parent(self, val: str):
        """Match object(s) by their parent Id

        - Nb. Links do not have a ParentId property.

        Args:
            val: an Id to match on

        Returns:
            self
        """
        self._parent = val
        return self

    def version_number(self, val: int):
        """Match version(s) by their version number.

        - Nb. Only Version objects have this property.

        Args:
            val: a number to match on

        Returns:
            self
        """
        self._versionnumber = val
        return self

    def item_type(self, val: str):
        """Match Item(s) by their item_type.

        - Nb. Only Item objects have this property.

        Args:
            val: a string to match on

        Returns:
            self
        """
        self._itemtype = val
        return self

    def item_variant(self, val):
        """Match Item(s) by their item_variant.

        - Nb. Only Item objects have this property.

        Args:
            val: a string to match on

        Returns:
            self
        """
        self._variant = val
        return self

    def has_facets(self, **kwargs):
        """Match objects on the given facets.

        Args:
            **kwargs:

        Returns:
            self
        """
        self._facets = copy.copy(kwargs)
        return self

    def name(self, val: str):
        """Set a name string to match objects on.

        - Nb. Collections, Resources and Links all have a 'name' property.

        Args:
            val:

        Returns:
            self
        """
        self._name = val
        return self

    def resource_type(self, val: str):
        """Set a resource type to match Resources on.

        - Nb. Only Resources have this property.

        Args:
            val:

        Returns:
            self
        """
        self._resourcetype = val
        return self

    def resource_location(self, val: str):
        """Set a location to match Resources on.

        - Nb. Only Resources have this property.

        Args:
            val:

        Returns:
            self
        """
        self._location = val
        return self

    def link_destination(self, val: str):
        """Set a link destination Id to match Links on.

        - Nb. Only Links have this property.

        Args:
            val:

        Returns:
            self
        """
        self._linkdst = val
        return self

    def link_source(self, val: str):
        """Set a link source Id to match Links on.

        - Nb. Only Links have this property.

        Args:
            val:

        Returns:
            self
        """
        self._linksrc = val
        return self

    def __repr__(self):
        return "<%s>" % self.__class__.__name__
