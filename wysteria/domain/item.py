"""

"""
import copy

from wysteria.domain.base import ChildWysObj
from wysteria.domain.query_desc import QueryDesc
from wysteria.domain.version import Version
from wysteria.domain.link import Link
import wysteria.constants as consts


class Item(ChildWysObj):
    def __init__(self, conn, data):
        super(Item, self).__init__()
        self.__conn = conn
        self._id = ""
        self._itemtype = ""
        self._variant = ""
        self._facets = {}

        self._load(data)

    @property
    def id(self):
        return self._id

    @property
    def item_type(self):
        return self._itemtype

    @property
    def variant(self):
        return self._variant

    @property
    def facets(self):
        return copy.copy(self._facets)

    def delete(self):
        """Delete this item. Children will be deleted too."""
        return self.__conn.delete_item(self.id)

    def get_linked_by_name(self, name):
        """Get linked Items by the link name

        Args:
            name (str):

        Returns:
            []domain.Item
        """
        if not name:
            return []

        # step 1: grab all links whose source is our id of the correct name
        link_query = [QueryDesc().link_source(self.id).name(name)]
        links = self.__conn.find_links(link_query)

        # step 2: grab all items whose id is the destination of one of our links
        item_query = [QueryDesc().id(l.destination) for l in links]
        return self.__conn.find_items(item_query)

    def get_linked(self):
        """Get all linked items and return a dict of link name (str) to []item

        Returns:
            dict
        """
        # step 1: grab all links whose source is our id
        link_query = [QueryDesc().link_source(self.id)]
        links = self.__conn.find_links(link_query)

        # step 2: build item query, and record item id -> link name map
        item_id_to_link_name = {}
        item_query = []
        for link in links:
            desired_item_id = link.destination
            item_id_to_link_name[desired_item_id] = link.name
            item_query.append(
                QueryDesc().id(link.destination)
            )

        # step 3: return matching item list
        items = self.__conn.find_items(item_query)

        # step 4: build into link name -> []item map
        result = {}
        for item in items:
            link_name = item_id_to_link_name.get(item.id)
            if not link_name:
                continue

            # ToDO: Rework into collections.defaultdict
            tmp = result.get(link_name, [])
            tmp.append(item)
            result[link_name] = tmp
        return result

    def link_to(self, name, item):
        """Create link between two items

        Args:
            name (str):
            item (domain.Item):

        """
        if not isinstance(item, self.__class__):
            return

        lnk = Link(
            self.__conn,
            {
                "src": self.id,
                "dst": item.id,
                "name": name,
            }
        )
        self.__conn.create_link(lnk)

    def update_facets(self, facets):
        """Set given key / value pairs in item facets

        Args:
            facets (dict):

        """
        self._facets.update(facets)
        self.__conn.update_item_facets(
            self.id,
            facets
        )

    def create_version(self, facets=None):
        """Create the next version obj for this item

        Args:
            facets (dict):

        Returns:
            domain.Version
        """
        if not facets:
            facets = {}

        parent_facets = self.facets
        required_facets = {
            consts.FACET_COLLECTION: parent_facets.get(consts.FACET_COLLECTION),
            consts.FACET_ITEM_TYPE: self.item_type,
            consts.FACET_ITEM_VARIANT: self.variant,
        }
        facets.update(required_facets)

        v = Version(self.__conn, {
            "parent": self.id,
            "facets": facets
        })

        vid, vnum = self.__conn.create_version(v)
        v._id = vid
        v._number = vnum
        return v

    def get_published(self):
        """

        Returns:
            domain.Version or None
        """
        return self.__conn.get_published_version(self.id)

    def _get_parent(self):
        """Return the parent item of this version

        Returns:
            domain.Item or None
        """
        results = self.__conn.find_items(
            [QueryDesc().id(self._parent)],
            limit=1,
        )
        if results:
            return results[0]
        return None
