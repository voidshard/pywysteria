"""

"""

from wysteria.domain.base import ChildWysObj
from wysteria.domain.query_desc import QueryDesc
from wysteria.domain.resource import Resource
from wysteria.domain.link import Link
from wysteria import constants as consts


class Version(ChildWysObj):

    def __init__(self, conn, **kwargs):
        super().__init__(**kwargs)
        self.__conn = conn
        self._number = kwargs.get("number")

    def __eq__(self, other):
        if not isinstance(other, Version):
            raise NotImplementedError()

        return all([
            self.id == other.id,
            self.parent == other.parent,
            self.version == other.version,
        ])

    @property
    def _default_child_facets(self) -> dict:
        """Returns some helpful default facets to set on child objects.

        Returns:
            dict
        """
        facets = {}
        for k, v in (
            (consts.FACET_COLLECTION, self.facets.get(consts.FACET_COLLECTION)),
            (consts.FACET_ITEM_TYPE, self.facets.get(consts.FACET_ITEM_TYPE)),
            (consts.FACET_ITEM_VARIANT, self.facets.get(consts.FACET_ITEM_VARIANT)),
            ("version", "%s" % self.version),
        ):
            if not v:
                continue

            facets[k] = v
        return facets

    def delete(self):
        """Delete this version."""
        return self.__conn.delete_version(self.id)

    def add_resource(self, name, resource_type, location, facets=None):
        """Create resource with given params as child of this version

        Args:
            name (str):
            resource_type (str):
            location (str):
            facets (dict): set some initial facets

        Returns:
            domain.Resource
        """
        cfacets = self._default_child_facets
        if facets:
            cfacets.update(facets)

        r = Resource(
            self.__conn,
            parent=self.id,
            name=name,
            resourcetype=resource_type,
            location=location,
            facets=cfacets,
        )
        r._id = self.__conn.create_resource(r)
        return r

    def get_resources(self, name=None, resource_type=None):
        """Return a list of resources associated with this version.

        Args:
            name (str): only return resources with the given name
            resource_type (str): only return resources with the given type

        Returns:
            []domain.Resource
        """
        query = QueryDesc().parent(self.id)
        if name:
            query.name(name)
        if resource_type:
            query.resource_type(resource_type)
        return self.__conn.find_resources([query])

    def get_linked_by_name(self, name):
        """Get linked Items by the link name

        Args:
            name (str):

        Returns:
            []domain.Version
        """
        if not name:
            return []

        # step 1: grab all links whose source is our id of the correct name
        link_query = [QueryDesc().link_source(self.id).name(name)]
        links = self.__conn.find_links(link_query)

        # step 2: grab all vers whose id is the destination of one of our links
        version_query = [QueryDesc().id(l.destination) for l in links]
        return self.__conn.find_versions(version_query)

    def get_linked(self):
        """Get all linked version and return a dict of link name (str) to
        []version

        Returns:
            dict
        """
        # step 1: grab all links whose source is our id
        link_query = [QueryDesc().link_source(self.id)]
        links = self.__conn.find_links(link_query)

        # step 2: build version query, and record version id -> link name map
        version_id_to_link_name = {}
        version_query = []
        for link in links:
            desired_version_id = link.destination
            version_id_to_link_name[desired_version_id] = link.name
            version_query.append(
                QueryDesc().id(link.destination)
            )

        # step 3: return matching version list
        versions = self.__conn.find_versions(version_query)

        # step 4: build into link name -> []version map
        result = {}
        for version in versions:
            link_name = version_id_to_link_name.get(version.id)
            if not link_name:
                continue

            # ToDO: Rework into collections.defaultdict
            tmp = result.get(link_name, [])
            tmp.append(version)
            result[link_name] = tmp
        return result

    def _fetch_uri(self) -> str:
        """Fetch uri from remote server.

        Returns:
            str
        """
        result = self.__conn.find_versions([QueryDesc().id(self.id)], limit=1)
        if result:
            return result[0].uri
        return ""

    def _encode(self) -> dict:
        """Encode this as a JSONifiable dict

        Returns:
            dict
        """
        return {
            "id": self.id,
            "uri": self._uri,
            "number": self.version,
            "parent": self.parent,
            "facets": self.facets,
        }

    def link_to(self, name, version, facets=None):
        """Create link between two versions

        Args:
            name (str):
            version (domain.Version):
            facets (dict): some defaults facets to add to link

        Raises:
            ValueError if given version not of type Version
        """
        if not isinstance(version, self.__class__):
            raise ValueError(
                f"Expected Versiob to be of type Version, got {version.__class__.__name__}"
            )

        cfacets = self._default_child_facets
        cfacets[consts.FACET_LINK_TYPE] = consts.VALUE_LINK_TYPE_VERSION
        if facets:
            cfacets.update(facets)

        lnk = Link(
            self.__conn,
            src=self.id,
            dst=version.id,
            name=name,
            facets=cfacets,
        )
        lnk._id = self.__conn.create_link(lnk)
        return lnk

    def publish(self):
        """Set this version as the published one"""
        self.__conn.publish_version(self.id)

    def _update_facets(self, facets):
        """Set given key / value pairs in version facets

        Args:
            facets (dict):

        """
        self.__conn.update_version_facets(
            self.id,
            facets
        )

    @property
    def version(self) -> int:
        """Return the version number of this version

        Returns:
            int
        """
        return self._number

    def _get_parent(self):
        """Return the parent item of this version

        Returns:
            domain.Item or None
        """
        results = self.__conn.find_items(
            [QueryDesc().id(self._parent)], limit=1
        )
        if results:
            return results[0]
        return None
