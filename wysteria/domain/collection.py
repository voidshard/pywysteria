"""

"""
from copy import copy

import wysteria.constants as consts
from wysteria.domain.base import ChildWysObj
from wysteria.domain.item import Item
from wysteria.domain.query_desc import QueryDesc


class Collection(ChildWysObj):

    def __init__(self, conn, **kwargs):
        super().__init__(**kwargs)
        self.__conn = conn
        self._name = kwargs.get("name")

    def _encode(self) -> dict:
        """Return the dict representation of this object

        Returns:
            dict
        """
        return {
            "id": self.id,
            "uri": self._uri,
            "name": self.name,
            "parent": self._parent,
            "facets": self.facets,
        }

    def __eq__(self, other):
        if not isinstance(other, Collection):
            raise NotImplementedError()

        return all([
            self.id == other.id,
            self.name == other.name,
            self.parent == other.parent,
        ])

    def _fetch_uri(self) -> str:
        """Fetch uri from remote server.

        Returns:
            str
        """
        result = self.__conn.find_collections([QueryDesc().id(self.id)], limit=1)
        if result:
            return result[0].uri
        return ""

    @property
    def name(self) -> str:
        """Return the name of this collection

        Returns:
            str
        """
        return self._name

    def delete(self):
        """Delete this collection. 
        """
        return self.__conn.delete_collection(self.id)

    def create_collection(self, name: str, facets: dict=None):
        """Create a sub collection of this collection

        Args:
            name (str): name of collection
            facets (dict): default facets to set on new collection

        Returns:
            domain.Collection
        """
        cfacets = copy(facets)
        if not cfacets:
            cfacets = {}

        cfacets[consts.FACET_COLLECTION] = cfacets.get(consts.FACET_COLLECTION, self.name)

        c = Collection(self.__conn, name=name, parent=self.id, facets=cfacets)
        c._id = self.__conn.create_collection(c)
        return c

    def _update_facets(self, facets: dict):
        """Performs the actual facet update via wysteria

        Args:
            facets: dict

        """
        self.__conn.update_collection_facets(self.id, facets)

    def get_collections(self, name: str=None):
        """Return child collections of this collection

        Args:
            name (str):

        Returns:
            []domain.Collection
        """
        query = QueryDesc().parent(self.id)
        if name:
            query.name(name)
        return self.__conn.find_collections([query])

    def create_item(self, item_type: str, variant: str, facets: dict=None) -> Item:
        """Create a child item with the given name & variant.

        Note a collection can only have one item with a given type & variant

        Args:
            item_type (str):
            variant (str):
            facets (dict):

        Returns:
            domain.Item
        """
        cfacets = copy(facets)
        if not cfacets:
            cfacets = {}

        cfacets[consts.FACET_COLLECTION] = self.name

        i = Item(
            self.__conn,
            parent=self.id,
            itemtype=item_type,
            variant=variant,
            facets=cfacets,
        )
        i._id = self.__conn.create_item(i)
        return i

    def get_items(self, item_type: str=None, variant: str=None):
        """Return all child items of this

        Args:
            item_type (str): only get item(s) of the given type
            variant (str): only get variant(s) of the given type

        Returns:
            []domain.Item
        """
        query = QueryDesc().parent(self.id)

        if item_type:
            query.item_type(item_type)

        if variant:
            query.item_variant(variant)

        return self.__conn.find_items([query])

    def _get_parent(self):
        """Return the parent Collection of this Collection

        Returns:
            domain.Collection or None
        """
        results = self.__conn.find_collections(
            [QueryDesc().id(self.parent)],
            limit=1
        )
        if results:
            return results[0]
        return None
