"""

"""
from copy import copy

from wysteria.middleware import NatsMiddleware
from wysteria import constants as consts
from wysteria.errors import UnknownMiddlewareError
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

    def __init__(self, url=None, middleware=_KEY_MIDDLEWARE_NATS, tls=None):
        """

        Args:
            url (str):
            middleware (str): the name of an available middleware
            tls: an ssl_ctx object (https://docs.python.org/3/library/ssl.html#context-creation)
        """
        cls = _AVAILABLE_MIDDLEWARES.get(middleware.lower())
        if not cls:
            raise UnknownMiddlewareError("Unknown middleware '%s'" % middleware)

        self._conn = cls(**{"url": url, "tls": tls})

    def connect(self):
        """Connect to wysteria - used if you do not wish to use 'with'
        """
        self._conn.connect()

    def close(self):
        """Disconnect from wysteria - used if you do not wish to use 'with'
        """
        try:
            self._conn.close()
        except Exception:
            pass  # prevent the middleware from raising when we call close on it

    def __enter__(self):
        """Connect to remote host(s)"""
        self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection(s) to remote host"""
        self.close()

    def search(self):
        """Start a new search

        Returns:
            wysteria.Search
        """
        return Search(self._conn)

    @property
    def default_middleware(self) -> str:
        """Return the default middleware name

        Returns:
            str
        """
        return _DEFAULT_MIDDLEWARE

    @staticmethod
    def available_middleware() -> list:
        """Return a list of the available middleware

        Returns:
            []str
        """
        return list(_AVAILABLE_MIDDLEWARES.keys())

    def create_collection(self, name: str, facets: dict=None):
        """Create a collection with the given name.

        Note: Only one collection is allowed with a given name.

        Args:
            name (str): name for new collection
            facets (dict): facets to set on new collection

        Returns:
            domain.Collection
        """
        cfacets = copy(facets)
        if not cfacets:
            cfacets = {}

        cfacets[consts.FACET_COLLECTION] = cfacets.get(consts.FACET_COLLECTION, "/")

        c = Collection(self._conn, name=name, facets=cfacets)
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
        ], limit=1)
        if not result:
            return None
        return result[0]

    def get_item(self, item_id):
        """Find & return an item by its ID

        Args:
            item_id (str):

        Returns:
            domain.Item or None
        """
        result = self._conn.find_items([
            QueryDesc().id(item_id),
        ], limit=1)
        if not result:
            return None
        return result[0]
