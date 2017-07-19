"""

"""
from wysteria.domain.base import WysBaseObj
from wysteria.domain.query_desc import QueryDesc
from wysteria.domain.item import Item
import wysteria.constants as consts


class Collection(WysBaseObj):
    def __init__(self, conn, data):
        self.__conn = conn
        self._id = ""
        self._name = ""
        self._parent = ""
        self._load(data)

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def delete(self):
        """Delete this collection. All children will be deleted too."""
        return self.__conn.delete_collection(self.id)

    def create_collection(self, name):
        """Create a sub collection of this collection

        Args:
            name (str): name of collection

        Returns:
            domain.Collection
        """
        c = Collection(self.__conn, {
            "name": name,
            "parent": self.id,
        })
        c._id = self.__conn.create_collection(c)
        return c

    def get_collections(self, name=None):
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

    def create_item(self, item_type, variant, facets=None):
        """Create a child item with the given name & variant.

        Note a collection can only have one item with a given type & variant

        Args:
            item_type (str):
            variant (str):
            facets (dict):

        Returns:
            domain.Item
        """
        if not facets:
            facets = {}

        required_facets = {
            consts.FACET_COLLECTION: self.name,
        }
        facets.update(required_facets)

        i = Item(self.__conn, {
            "parent": self.id,
            "itemtype": item_type,
            "variant": variant,
            "facets": facets,
        })
        i._id = self.__conn.create_item(i)
        return i

    def get_items(self, item_type=None, variant=None):
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
