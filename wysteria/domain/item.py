"""

"""
import wysteria.constants as consts
from wysteria.domain.base import ChildWysObj
from wysteria.domain.query_desc import QueryDesc
from wysteria.domain.version import Version
from wysteria.domain.link import Link


class Item(ChildWysObj):

    def __init__(self, conn, **kwargs):
        super().__init__(**kwargs)
        self.__conn = conn
        self._itemtype = kwargs.get("itemtype", "")
        self._variant = kwargs.get("variant", "")

    def __eq__(self, other):
        if not isinstance(other, Item):
            raise NotImplementedError()

        return all([
            self.id == other.id,
            self.parent == other.parent,
            self.item_type == other.item_type,
            self.variant == other.variant,
            self.parent == other.parent,
            self.facets == other.facets,
        ])

    def _encode(self) -> dict:
        """Return a dict representation of this Item

        Returns:
            dict
        """
        return {
            "id": self.id,
            "parent": self._parent,
            "facets": self.facets,
            "itemtype": self._itemtype,
            "variant": self._variant,
        }

    @property
    def item_type(self) -> str:
        """Return the item type for this Item

        Returns:
            str
        """
        return self._itemtype

    @property
    def variant(self) -> str:
        """Return the item variant of this Item

        Returns:
            str
        """
        return self._variant

    def delete(self):
        """Delete this item."""
        return self.__conn.delete_item(self.id)

    def get_linked_by_name(self, name: str):
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

    def get_linked(self) -> dict:
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

    def link_to(self, name: str, item) -> Link:
        """Create link between two items

        Args:
            name (str):
            item (domain.Item):

        Returns:
            Link

        Raises:
            ValueError if given item not of type Item
        """
        if not isinstance(item, self.__class__):
            raise ValueError(f"Expected item to be of type Item, got {item.__class__.__name__}")

        lnk = Link(
            self.__conn,
            src=self.id,
            dst=item.id,
            name=name,
            facets={consts.FACET_LINK_TYPE: consts.VALUE_LINK_TYPE_ITEM}
        )
        lnk._id = self.__conn.create_link(lnk)
        return lnk

    def _update_facets(self, facets: dict):
        """Set given key / value pairs in item facets

        Args:
            facets: facets to update
        """
        self.__conn.update_item_facets(self.id, facets)

    def create_version(self, facets: dict=None) -> Version:
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

        v = Version(
            self.__conn,
            parent=self.id,
            facets=facets
        )

        vid, vnum = self.__conn.create_version(v)
        v._id = vid
        v._number = vnum
        return v

    def get_published(self) -> Version:
        """Gvet the current published version of this Item, if any

        Returns:
            domain.Version or None
        """
        return self.__conn.get_published_version(self.id)

    def _get_parent(self):
        """Return the parent item of this version

        Returns:
            domain.Collection or None
        """
        results = self.__conn.find_collections(
            [QueryDesc().id(self._parent)],
            limit=1,
        )
        if results:
            return results[0]
        return None
