import abc


class WysBaseObj(object):
    """
    Represents a wysteria obj in the most general sense
    """
    def encode(self):
        """Return a dict version of the object

        Returns:
            dict
        """
        data = {}
        for k, v in self.__dict__.iteritems():
            if "__" in k:
                continue
            data[k.lstrip("_")] = v
        return data

    def _load(self, data):
        """Set internal values given a dict of values

        Args:
            data (dict):

        Returns:
            self
        """
        if not data:
            return

        for k, v in data.iteritems():
            key = "_%s" % k.lower()
            if hasattr(self, key) and not getattr(self, key):
                setattr(self, key, v)

    def __str__(self):
        return str(self.encode())

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.id)


class ChildWysObj(WysBaseObj):
    """
    Represents a wysteria obj that has a parent obj
    """
    def __init__(self):
        self.__cached_parent_obj = None
        self._parent = ""

    @property
    def parent(self):
        """Return the ID of this object's parent

        Returns:
            str
        """
        return self._parent

    @abc.abstractmethod
    def _get_parent(self):
        """

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
