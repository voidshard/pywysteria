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
        self._load(data)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def delete(self):
        """Delete this collection. All children will be deleted too."""
        return self.__conn.delete_collection(self.id)

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
