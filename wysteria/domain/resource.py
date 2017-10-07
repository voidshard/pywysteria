"""

"""

from wysteria.domain.base import ChildWysObj
from wysteria.domain.query_desc import QueryDesc


class Resource(ChildWysObj):
    def __init__(self, conn, data):
        super(Resource, self).__init__()
        self.__conn = conn
        self._id = ""
        self._parent = ""
        self._resourcetype = ""
        self._name = ""
        self._location = ""
        self._load(data)

    @property
    def id(self):
        return self._id

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
