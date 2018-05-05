import abc
import copy


class WysBaseObj(metaclass=abc.ABCMeta):
    """
    Represents a wysteria obj in the most general sense
    """

    def __init__(self, **kwargs):
        self._id = kwargs.get("id", "")
        self._uri = kwargs.get("uri", "")
        self._facets = kwargs.get("facets", {})

    def encode(self) -> dict:
        """Encode this obj into a dict

        Returns:
            dict
        """
        return copy.copy(self._encode())

    @abc.abstractmethod
    def _encode(self) -> dict:
        """Return a dict version of the object

        Returns:
            dict
        """
        pass

    @property
    def id(self) -> str:
        """Return the ID of this object

        Returns:
            str
        """
        return self._id

    @abc.abstractmethod
    def _fetch_uri(self) -> str:
        """Fetch uri from remote server.

        Returns:
            str
        """
        # Nb. This property is the only one we don't know on creation as it's determined on the
        # server and isn't auto returned.
        pass

    @property
    def uri(self) -> str:
        """Return the unique URI for this object.

        Returns:
            str

        Raises:
            ValueError if the URI cannot be found / constructed
        """
        if not self._uri:
            self._uri = self._fetch_uri()

        if not self._uri:
            raise ValueError("Unable to fetch URI")

        return self._uri

    @property
    def facets(self) -> dict:
        """Return a copy of this object's facets

        Returns:
            dict
        """
        return copy.copy(self._facets)

    def update_facets(self, **kwargs):
        """Update this object's facets with the give key / values pairs.

        Args:
            **kwargs:

        Raises:
            RequestTimeoutError
        """
        if not kwargs:
            return

        self._update_facets(kwargs)
        self._facets.update(kwargs)

    @abc.abstractmethod
    def _update_facets(self, facets):
        """Perform the actual wysteria call to update facets.

        Args:
            facets (dict):

        """
        pass

    def __str__(self):
        return str(self.encode())

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.id)


class ChildWysObj(WysBaseObj):
    """
    Represents a wysteria obj that has a parent obj
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__cached_parent_obj = None
        self._parent = kwargs.get("parent", "")

    @property
    def parent(self):
        """Return the ID of this object's parent

        Returns:
            str
        """
        return self._parent

    @abc.abstractmethod
    def _get_parent(self):
        """Return the parent obj of this object.

        Returns:
            sub class of WysBaseObj
        """
        pass

    def get_parent(self):
        """Return the parent collection of this item

        Returns:
            sub class of WysBaseObj or None
        """
        if not self.__cached_parent_obj:
            self.__cached_parent_obj = self._get_parent()
        return self.__cached_parent_obj
