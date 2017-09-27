import json
import tornado
import threading
from Queue import Queue, Empty

from nats.io.client import Client

from abstract_dao import WysteriaConnectionBase
from wysteria import domain
from wysteria.constants import DEFAULT_QUERY_LIMIT
from wysteria.errors import RequestTimeoutError


_DEFAULT_URI = "nats://localhost:4222"  # default localhost, nats port
_CLIENT_ROUTE = "w.client.%s"  # From a client

# wysteria nats protocol routes 
_KEY_CREATE_COLLECTION = _CLIENT_ROUTE % "cc"
_KEY_CREATE_ITEM = _CLIENT_ROUTE % "ci"
_KEY_CREATE_VERSION = _CLIENT_ROUTE % "cv"
_KEY_CREATE_RESOURCE = _CLIENT_ROUTE % "cr"
_KEY_CREATE_LINK = _CLIENT_ROUTE % "cl"

_KEY_DELETE_COLLECTION = _CLIENT_ROUTE % "dc"
_KEY_DELETE_ITEM = _CLIENT_ROUTE % "di"
_KEY_DELETE_VERSION = _CLIENT_ROUTE % "dv"
_KEY_DELETE_RESOURCE = _CLIENT_ROUTE % "dr"

_KEY_FIND_COLLECTION = _CLIENT_ROUTE % "fc"
_KEY_FIND_ITEM = _CLIENT_ROUTE % "fi"
_KEY_FIND_VERSION = _CLIENT_ROUTE % "fv"
_KEY_FIND_RESOURCE = _CLIENT_ROUTE % "fr"
_KEY_FIND_LINK = _CLIENT_ROUTE % "fl"

_KEY_GET_PUBLISHED = _CLIENT_ROUTE % "gp"
_KEY_SET_PUBLISHED = _CLIENT_ROUTE % "sp"

_KEY_UPDATE_ITEM = _CLIENT_ROUTE % "ui"
_KEY_UPDATE_VERSION = _CLIENT_ROUTE % "uv"


NATS_MSG_RETRIES = 3
NATS_MSG_TIMEOUT = 2


def _retry(func):
    """Simple wrapper func that retries the given func some number of times
    on any exception(s).

    Warning: Care should be taken only to use this on idempotent functions only

    Args:
        func:

    Returns:
        ?
    """
    def retry_func(*args, **kwargs):
        for count in range(0, NATS_MSG_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except (RequestTimeoutError, Empty) as e:
                if count >= NATS_MSG_RETRIES:
                    raise
    return retry_func


class _TornadoNats(threading.Thread):
    """
    Tiny class to handle queuing requests through tornado.
    """
    _MAX_RECONNECTS = 10

    def __init__(self, url):
        threading.Thread.__init__(self)
        self._conn = None
        self._url = url
        self._outgoing = Queue()
        self._running = False

    @tornado.gen.coroutine
    def main(self):
        """Connect to remote host(s)

        Raises:
            Exception if unable to establish connection to remote host(s)
        """
        self._conn = Client()
        yield self._conn.connect(
            servers=[self._url],
            allow_reconnect=True,
            max_reconnect_attempts=self._MAX_RECONNECTS
        )
        while self._running:
            while not self._outgoing.empty():
                reply_queue, key, data = self._outgoing.get()
                result = yield self._conn.timed_request(key, data)
                reply_queue.put(result.data)

    def request(self, data, key, timeout=5):
        q = Queue(maxsize=NATS_MSG_RETRIES)
        self._outgoing.put((q, key, data))
        try:
            return q.get(timeout=timeout)
        except Empty as e:
            return RequestTimeoutError("Timeout waiting for server reply. Original %s" % e)

    def stop(self):
        self._running = False
        try:
            self._conn.flush()
            self._conn.close()
        except Exception as e:
            pass

    def run(self):
        if self._running:
            return

        self._running = True
        tornado.ioloop.IOLoop.instance().run_sync(self.main)


class WysteriaNatsMiddleware(WysteriaConnectionBase):
    """
    Wysteria middleware client using Nats.io to manage transport

    Using python nats client (copied & modified in libs/ dir)
    https://github.com/jackytu/python-nats/blob/master/nats/client.py
    """
    def __init__(self, url=_DEFAULT_URI):
        """Construct new client

        Url as in "nats://user:password@host:port"

        Args:
            url (str):
        """
        self._conn = None
        self._url = url

    def connect(self):
        """Connect to remote host(s)

        Raises:
            Exception if unable to establish connection to remote host(s)
        """
        self._conn = _TornadoNats(self._url)
        self._conn.setDaemon(True)
        self._conn.start()

    def close(self):
        """Close remote connection"""
        self._conn.stop()

    @_retry
    def _sync_idempotent_msg(self, data, key, timeout=3):
        """Send an idempotent message to the server and wait for a reply.

        This will be retried on failure(s) up to NATS_MSG_RETRIES times.

        Args:
            data (dict): json data to send
            key (str): message subject
            timeout (int): seconds to wait for reply

        Returns:
            dict

        Raises:
            RequestTimeoutError
        """
        return self._single_request(data, key, timeout=timeout)

    def _single_request(self, data, key, timeout=5):
        if not isinstance(data, str):
            data = json.dumps(data)
            
        reply = self._conn.request(data, key, timeout=timeout)
        return json.loads(reply)

    def _generic_find(self, query, key, limit, offset):
        """Send a find query to the server, return results (if any)

        Args:
            query ([domain.QueryDesc]):
            key (str):
            limit (int):
            offset (int):

        Returns:
            []dict

        Raises:
            Exception on server err
        """
        data = {
            "query": [q.encode() for q in query if q.is_valid],
            "limit": limit,
            "offset": offset,
        }

        reply = self._sync_idempotent_msg(data, key)

        err_msg = reply.get("Error")
        if err_msg:  # wysteria replied with an err, we should raise it
            raise Exception(err_msg)

        return reply.get("All", [])

    def find_collections(self, query, limit=DEFAULT_QUERY_LIMIT, offset=0):
        """Query server & return type appropriate matching results

        Args:
            query ([]domain.QueryDesc): search query(ies) to execute
            limit (int): limit number of returned results
            offset (int): return results starting from some offset

        Returns:
            []domain.Collection

        Raises:
            Exception on network / server error
        """
        return [
            domain.Collection(self, c) for c in self._generic_find(
                query, _KEY_FIND_COLLECTION, limit, offset
            )
        ]

    def find_items(self, query, limit=DEFAULT_QUERY_LIMIT, offset=0):
        """Query server & return type appropriate matching results

        Args:
            query ([]domain.QueryDesc): search query(ies) to execute
            limit (int): limit number of returned results
            offset (int): return results starting from some offset

        Returns:
            []domain.Item

        Raises:
            Exception on network / server error
        """
        return [
            domain.Item(self, c) for c in self._generic_find(
                query, _KEY_FIND_ITEM, limit, offset
            )
        ]
    
    def find_versions(self, query, limit=DEFAULT_QUERY_LIMIT, offset=0):
        """Query server & return type appropriate matching results

        Args:
            query ([]domain.QueryDesc): search query(ies) to execute
            limit (int): limit number of returned results
            offset (int): return results starting from some offset

        Returns:
            []domain.Version

        Raises:
            Exception on network / server error
        """
        return [
            domain.Version(self, c) for c in self._generic_find(
                query, _KEY_FIND_VERSION, limit, offset
            )
        ]

    def find_resources(self, query, limit=DEFAULT_QUERY_LIMIT, offset=0):
        """Query server & return type appropriate matching results

        Args:
            query ([]domain.QueryDesc): search query(ies) to execute
            limit (int): limit number of returned results
            offset (int): return results starting from some offset

        Returns:
            []domain.Resource

        Raises:
            Exception on network / server error
        """
        return [
            domain.Resource(self, c) for c in self._generic_find(
                query, _KEY_FIND_RESOURCE, limit, offset
            )
        ]

    def find_links(self, query, limit=DEFAULT_QUERY_LIMIT, offset=0):
        """Query server & return type appropriate matching results

        Args:
            query ([]domain.QueryDesc): search query(ies) to execute
            limit (int): limit number of returned results
            offset (int): return results starting from some offset

        Returns:
            []domain.Link

        Raises:
            Exception on network / server error
        """
        return [
            domain.Link(self, c) for c in self._generic_find(
                query, _KEY_FIND_LINK, limit, offset
            )
        ]
    
    def get_published_version(self, oid):
        """Item ID to find published version for

        Args:
            oid (str): item id to find published version for

        Returns:
            wysteria.domain.Version or None

        Raises:
            Exception on network / server error
        """
        reply = self._sync_idempotent_msg(
            {"id": oid}, _KEY_GET_PUBLISHED
        )

        err_msg = reply.get("Error")
        if err_msg:
            raise Exception(err_msg)

        data = reply.get("Version", None)
        if not data:
            return None

        return domain.Version(self, data)

    def publish_version(self, oid):
        """Version ID mark as published

        Args:
            oid (str): version id to publish

        Raises:
            Exception on network / server error
        """
        reply = self._sync_idempotent_msg(
            {"id": oid}, _KEY_SET_PUBLISHED
        )

        err_msg = reply.get("Error")
        if err_msg:
            raise Exception(err_msg)

    def _sync_update_facets_msg(self, oid, facets, key, find_func):
        """

        Args:
            oid (str):
            facets (dict):
            key (str):
            find_func (func): function (str, str) -> []Version or []Item

        Raises:
            Exception on network / server error
        """
        data = json.dumps({
            "id": oid,
            "facets": facets,
        })
        find_self = [domain.QueryDesc().id(oid)]

        reply = {}
        for count in range(0, NATS_MSG_RETRIES + 1):
            # Fire the update request to wysteria
            try:
                reply = self._single_request(data, key)
                break  # if nothing goes wrong, we break out of the loop
            except (RequestTimeoutError, Empty) as e:
                if count >= NATS_MSG_RETRIES:
                    raise

            # We sent an Update and it broke, let's not retry unless our
            # change *didn't* go through
            retry = False
            matching_wysteria_objects = find_func(find_self)
            if not matching_wysteria_objects:
                break  # the obj has been deleted / id invalid? Let's break

            # Check if the keys we want to set are set already
            matching_obj = matching_wysteria_objects[0]
            for key, value in facets.iteritems():
                if matching_obj.facets.get(key, "") != str(value):
                    retry = True
                    break

            # if all our desired facets are now set, then we can break out
            if not retry:
                break

        err_msg = reply.get("Error")
        if err_msg:
            raise Exception(err_msg)

    def update_version_facets(self, oid, facets):
        """Update version with matching ID with given facets.

        This is smart enough to only retry failed updates if the given update
        didn't set the desired fields when it failed.

        It's not perfect, but should be serviceable.

        Args:
            oid (str): version ID to update
            facets (dict): new facets (these are added to existing facets)

        Raises:
            Exception on network / server error
        """
        self._sync_update_facets_msg(
            oid,
            facets,
            _KEY_UPDATE_VERSION,
            self.find_versions
        )

    def update_item_facets(self, oid, facets):
        """Update item with matching ID with given facets

        Args:
            oid (str): item ID to update
            facets (dict): new facets (these are added to existing facets)

        Raises:
            Exception on network / server error
        """
        self._sync_update_facets_msg(
            oid,
            facets,
            _KEY_UPDATE_ITEM,
            self.find_items
        )

    def _generic_create(self, request_data, find_query, key, find_func, timeout=3):
        """Creation requests for
         - collection
         - item
         - resource
         - link
        Are similar enough that we can refactor their create funcs into one.
        Versions however, are a different animal.

        Args:
            request_data (dict): json data to send as creation request
            find_query ([]domain.QueryDesc): query to uniquely find the obj
            key (str): nats subject to send
            find_func: function to find desired obj
            timeout (float): time to wait before retry

        Returns:
            str
        """
        reply = {}
        for count in range(0, NATS_MSG_RETRIES + 1):
            # send creation request
            try:
                reply = self._single_request(request_data, key)
                break  # if nothing went wrong, we've created it successfully
            except (RequestTimeoutError, Empty) as e:
                if count >= NATS_MSG_RETRIES:
                    raise

            # something went wrong, see if we created item
            results = find_func(find_query)
            if not results:
                continue  # we didn't create it, try again

            # We did create it, return the id
            return results[0].id

        err_msg = reply.get("Error")
        if err_msg:
            raise Exception(err_msg)

        return reply.get("Id")

    def create_collection(self, collection):
        """Create collection with given name, return ID of new collection

        Args:
            collection (domain.Collection):

        Returns:
            str
        """
        data = json.dumps({
            "Collection": collection.encode(),
        })
        find_query = [
            domain.QueryDesc()
                .name(collection.name)
                .parent(collection.parent)
        ]
        return self._generic_create(
            data,
            find_query,
            _KEY_CREATE_COLLECTION,
            self.find_collections
        )
    
    def create_item(self, item):
        """Create item with given values, return ID of new item

        Args:
            item (wysteria.domain.Item): input item

        Returns:
            str

        Raises:
            Exception on network / server error
        """
        data = json.dumps({
            "Item": item.encode(),
        })
        find_query = [
            domain.QueryDesc()
                .item_type(item.item_type)
                .item_variant(item.variant)
                .parent(item.parent)
        ]
        return self._generic_create(
            data,
            find_query,
            _KEY_CREATE_ITEM,
            self.find_items
        )

    def create_version(self, version):
        """Create item with given values, return ID of new version

        Args:
            version (wysteria.domain.Version): input version

        Returns:
            str, int

        Raises:
            Exception on network / server error
        """
        # We can't uniquely identify the version we're hoping to create as the
        # server will increment the version number for us.
        # We could have the wysteria server implement a version reservation
        # scheme, but since we usually only care about the published version
        # we're just going to try again ..
        # ToDo: Consider version number reservation
        reply = self._sync_idempotent_msg(
            {
                "Version": version.encode(),
            },
            _KEY_CREATE_VERSION
        )

        err_msg = reply.get("Error")
        if err_msg:
            raise Exception(err_msg)

        return reply.get("Id"), reply.get("Version")
    
    def create_resource(self, resource):
        """Create item with given values, return ID of new resource

        Args:
            resource (wysteria.domain.Resource): input resource

        Returns:
            str

        Raises:
            Exception on network / server error
        """
        data = json.dumps({
            "Resource": resource.encode(),
        })
        find_query = [
            domain.QueryDesc()
                .resource_type(resource.resource_type)
                .name(resource.name)
                .resource_location(resource.location)
                .parent(resource.parent)
        ]
        return self._generic_create(
            data,
            find_query,
            _KEY_CREATE_RESOURCE,
            self.find_resources
        )
    
    def create_link(self, link):
        """Create item with given values, return ID of new link

        Args:
            link (wysteria.domain.Link): input link

        Returns:
            str

        Raises:
            Exception on network / server error
        """
        data = json.dumps({
            "Link": link.encode(),
        })
        find_query = [
            domain.QueryDesc()
                .link_source(link.source)
                .link_destination(link.destination)
        ]
        return self._generic_create(
            data,
            find_query,
            _KEY_CREATE_LINK,
            self.find_links
        )

    def _generic_delete(self, oid, key):
        """Call remote delete function with given params

        Args:
            oid (str):
            key (str):

        Returns:
            None

        Raises:
            Exception on any network / server err
        """
        reply = self._sync_idempotent_msg(
            {"id": oid}, key
        )

        err_msg = reply.get("Error")
        if err_msg:
            raise Exception(err_msg)

    def delete_collection(self, oid):
        """Delete the matching obj type with the given id

        Args:
            oid (str): id of obj to delete

        Raises:
            Exception if deletion fails / network error
        """
        self._generic_delete(oid, _KEY_DELETE_COLLECTION)

    def delete_item(self, oid):
        """Delete the matching obj type with the given id

        (Links will be deleted automatically)

        Args:
            oid (str): id of obj to delete

        Raises:
            Exception if deletion fails / network error
        """
        self._generic_delete(oid, _KEY_DELETE_ITEM)
    
    def delete_version(self, oid):
        """Delete the matching obj type with the given id

        (Links will be deleted automatically)

        Args:
            oid (str): id of obj to delete

        Raises:
            Exception if deletion fails / network error
        """
        self._generic_delete(oid, _KEY_DELETE_VERSION)

    def delete_resource(self, oid):
        """Delete the matching obj type with the given id

        Args:
            oid (str): id of obj to delete

        Raises:
            Exception if deletion fails / network error
        """
        self._generic_delete(oid, _KEY_DELETE_RESOURCE)
