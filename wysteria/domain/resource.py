"""

"""

from wysteria.domain.base import ChildWysObj
from wysteria.domain.query_desc import QueryDesc


class Resource(ChildWysObj):

    def __init__(self, conn, **kwargs):
        super().__init__(**kwargs)
        self.__conn = conn
        self._resourcetype = kwargs.get("resourcetype")
        self._name = kwargs.get("name")
        self._location = kwargs.get("location")

    def __eq__(self, other):
        if not isinstance(other, Resource):
            raise NotImplementedError()

        return all([
            self.id == other.id,
            self.parent == other.parent,
            self.name == other.name,
            self.resource_type == other.resource_type,
            self.location == other.location,
        ])

    @property
    def resource_type(self) -> str:
        """Return the type of this resource

        Returns:
            str
        """
        return self._resourcetype

    def delete(self):
        """Delete this resource."""
        return self.__conn.delete_resource(self.id)

    @property
    def name(self) -> str:
        """Return the name of this resource

        Returns:
            str
        """
        return self._name

    @property
    def location(self) -> str:
        """Return the location URI of this resource

        Returns:
            str
        """
        return self._location

    def _get_parent(self):
        """Return the parent item of this version

        Returns:
            domain.Item or None
        """
        results = self.__conn.find_versions(
            [QueryDesc().id(self._parent)], limit=1
        )
        if results:
            return results[0]
        return None

    def _fetch_uri(self) -> str:
        """Fetch uri from remote server.

        Returns:
            str
        """
        result = self.__conn.find_resources([QueryDesc().id(self.id)], limit=1)
        if result:
            return result[0].uri
        return ""

    def _encode(self) -> dict:
        """Encode this resource as a dict

        Returns:
            duct
        """
        return {
            "id": self.id,
            "uri": self._uri,
            "parent": self.parent,
            "name": self.name,
            "resourcetype": self.resource_type,
            "location": self.location,
            "facets": self.facets,
        }

    def _update_facets(self, facets: dict):
        """Update this resource facets with the given facets

        Args:
            facets (dict):

        """
        self.__conn.update_resource_facets(self.id, facets)
