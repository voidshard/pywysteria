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
            self.facets == other.facets,
        ])

    @property
    def resource_type(self):
        return self._resourcetype

    @property
    def name(self):
        return self._name

    @property
    def location(self):
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

    def _encode(self):
        """

        Returns:
            duct
        """
        return {
            "id": self.id,
            "parent": self.parent,
            "name": self.name,
            "resourcetype": self.resource_type,
            "location": self.location,
            "facets": self.facets,
        }

    def _update_facets(self, facets):
        self.__conn.update_resource_facets(self.id, facets)
