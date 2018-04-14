"""

"""
from wysteria.domain.base import WysBaseObj


class Link(WysBaseObj):
    def __init__(self, conn, **kwargs):
        super().__init__(**kwargs)
        self.__conn = conn
        self._name = kwargs.get("name")
        self._src = kwargs.get("src")
        self._dst = kwargs.get("dst")

    def __eq__(self, other):
        if not isinstance(other, Link):
            raise NotImplementedError()

        return all([
            self.id == other.id,
            self.name == other.name,
            self.source == other.source,
            self.destination == other.destination,
            self.facets == other.facets,
        ])

    def _encode(self) -> dict:
        """Return dict representation of this link

        Returns:
            dict
        """
        return {
            "name": self.name,
            "src": self.source,
            "dst": self.destination,
            "facets": self.facets,
        }

    def _update_facets(self, facets: dict):
        """Call wysteria to update this link with the given facets

        Args:
            facets: dict
        """
        self.__conn.update_link_facets(self.id, facets)

    @property
    def id(self) -> str:
        """Return the ID of this link

        Returns:
            str
        """
        return self._id

    @property
    def name(self) -> str:
        """Return the name of this link

        Returns:
            str
        """
        return self._name

    @property
    def source(self) -> str:
        """Return the Id of the source object for this link.

        - Note that this could be either a Version or an Item Id.

        Returns:
            str
        """
        return self._src

    @property
    def destination(self) -> str:
        """Return the Id of the destination object for this link.

        - Note that this could be either a Version or an Item Id.

        Returns:
            str
        """
        return self._dst
