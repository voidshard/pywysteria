"""

"""

from wysteria.middleware import NatsMiddleware
from wysteria.errors import UnknownMiddleware
from wysteria.domain import Collection, QueryDesc
from wysteria.search import Search


_KEY_MIDDLEWARE_NATS = "nats"
_AVAILABLE_MIDDLEWARES = {
    _KEY_MIDDLEWARE_NATS: NatsMiddleware,
}
_DEFAULT_MIDDLEWARE = _KEY_MIDDLEWARE_NATS


class Client(object):
    """
    WysteriaClient wraps a middleware class and provides convenience.

    Although technically the middleware could be used directly, this
    client allows us to alter the middleware later on without needing to change
    anything client facing.
    """

    def __init__(self, url=None, middleware=_KEY_MIDDLEWARE_NATS):
        """

        Args:
            url (str):
            middleware (str): the name of an available middleware
        """
        cls = _AVAILABLE_MIDDLEWARES.get(middleware.lower())
        if not cls:
            raise UnknownMiddleware("Unknown middleware '%s'" % middleware)

        if url:
            self._conn = cls(url=url)
        else:
            self._conn = cls()

    def connect(self):
        """Connect to wysteria - used if you do not wish to use 'with'
        """
        try:
            self._conn.close()
        except:
            pass
        self._conn.connect()

    def close(self):
        """Disconnect from wysteria - used if you do not wish to use 'with'
        """
        self._conn.close()

    def __enter__(self):
        """Connect to remote host(s)"""
        try:
            self._conn.close()
        except:
            pass
        self._conn.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection(s) to remote host"""
        self._conn.close()

    def search(self):
        """Start a new search

        Returns:
            wysteria.Search
        """
        return Search(self._conn)

    @property
    def default_middleware(self):
        """Return the default middleware name

        Returns:
            str
        """
        return _DEFAULT_MIDDLEWARE

    @staticmethod
    def available_middleware():
        """Return a list of the available middleware

        Returns:
            []str
        """
        return _AVAILABLE_MIDDLEWARES.keys()

    def create_collection(self, name):
        """Create a collection with the given name.

        Note: Only one collection is allowed with a given name.

        Args:
            name (str): name for new collection

        Returns:
            domain.Collection
        """
        c = Collection(self._conn, {"name": name})
        c._id = self._conn.create_collection(c)
        return c

    def get_collection(self, identifier):
        """Find a collection by either name or id

        Args:
            identifier (str): either the name or id of the desired collection

        Returns:
            domain.Collection or None
        """
        result = self._conn.find_collections([
            QueryDesc().id(identifier),
            QueryDesc().name(identifier),
        ])
        if not result:
            return None
        return result[0]
