
"""

"""
from wysteria.domain.base import WysBaseObj


class Link(WysBaseObj):
    def __init__(self, conn, data):
        self.__conn = conn
        self._id = ""
        self._name = ""
        self._src = ""
        self._dst = ""
        self._load(data)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._src

    @property
    def destination(self):
        return self._dst
