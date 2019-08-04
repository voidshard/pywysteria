import abc

from wysteria import constants as consts
from wysteria import errors


class WysteriaConnectionBase(metaclass=abc.ABCMeta):
    """
    Abstract class to represent clientside wysteria middleware

    Pretty much a python clone of the wysteria/common/middleware client
    interface. Valid python clients should subclass from this.
    """

    @staticmethod
    def translate_server_exception(msg):
        """Turn a wysteria error string into a python exception.

        Args:
            msg: error string from wysteria

        Raises:
            AlreadyExistsError
            NotFoundError
            InvalidInputError
            IllegalOperationError
            ServerUnavailableError
            Exception
        """
        if consts.ERR_ALREADY_EXISTS in msg:
            raise errors.AlreadyExistsError(msg)
        elif consts.ERR_NOT_FOUND in msg:
            raise errors.NotFoundError(msg)
        elif consts.ERR_ILLEGAL in msg:
            raise errors.IllegalOperationError(msg)
        elif any([consts.ERR_INVALID in msg, "ffjson error" in msg]):
            raise errors.InvalidInputError(msg)
        elif consts.ERR_NOT_SERVING in msg:
            raise errors.ServerUnavailableError(msg)

        # something very unexpected happened
        raise Exception(msg)

    @abc.abstractmethod
    def connect(self):
        """Connect to remote host(s)

        Raises:
            Exception if unable to establish connection to remote host(s)
        """
        pass

    @abc.abstractmethod
    def close(self):
        """Close remote connection"""
        pass

    @abc.abstractmethod
    def find_collections(self, query, limit=None, offset=None):
        """Query server & return type appropriate matching results

        Args:
            query ([]domain.wysteria.QueryDesc): search query(ies) to execute
            limit (int): limit number of returned results
            offset (int): return results starting from some offset

        Returns:
            []domain.wysteria.Collection

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def find_items(self, query, limit=None, offset=None):
        """Query server & return type appropriate matching results

        Args:
            query ([]domain.wysteria.QueryDesc): search query(ies) to execute
            limit (int): limit number of returned results
            offset (int): return results starting from some offset

        Returns:
            []domain.wysteria.Item

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def find_versions(self, query, limit=None, offset=None):
        """Query server & return type appropriate matching results

        Args:
            query ([]domain.wysteria.QueryDesc): search query(ies) to execute
            limit (int): limit number of returned results
            offset (int): return results starting from some offset

        Returns:
            []domain.wysteria.Version

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def find_resources(self, query, limit=None, offset=None):
        """Query server & return type appropriate matching results

        Args:
            query ([]domain.wysteria.QueryDesc): search query(ies) to execute
            limit (int): limit number of returned results
            offset (int): return results starting from some offset

        Returns:
            []domain.wysteria.Resource

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def find_links(self, query, limit=None, offset=None):
        """Query server & return type appropriate matching results

        Args:
            query ([]domain.wysteria.QueryDesc): search query(ies) to execute
            limit (int): limit number of returned results
            offset (int): return results starting from some offset

        Returns:
            []domain.wysteria.Link

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def get_published_version(self, oid):
        """Item ID to find published version for

        Args:
            oid (str): item id to find published version for

        Returns:
            wysteria.domain.Version or None

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def publish_version(self, oid):
        """Version ID mark as published

        Args:
            oid (str): version id to publish

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def update_collection_facets(self, oid, facets):
        """Update collection with matching ID with given facets

        Args:
            oid (str): collection ID to update
            facets (dict): new facets (these are added to existing facets)

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def update_version_facets(self, oid, facets):
        """Update version with matching ID with given facets

        Args:
            oid (str): version ID to update
            facets (dict): new facets (these are added to existing facets)

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def update_item_facets(self, oid, facets):
        """Update item with matching ID with given facets

        Args:
            oid (str): item ID to update
            facets (dict): new facets (these are added to existing facets)

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def update_resource_facets(self, oid, facets):
        """Update resource with matching ID with given facets

        Args:
            oid (str): resource ID to update
            facets (dict): new facets (these are added to existing facets)

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def update_link_facets(self, oid, facets):
        """Update link with matching ID with given facets

        Args:
            oid (str): link ID to update
            facets (dict): new facets (these are added to existing facets)

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def create_collection(self, collection):
        """Create collection with given name, return ID of new collection

        Args:
            collection (wysteria.domain.Collection): input collection

        Returns:
            str
        """
        pass
    
    @abc.abstractmethod
    def create_item(self, item):
        """Create item with given values, return ID of new item

        Args:
            item (wysteria.domain.Item): input item

        Returns:
            str

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def create_version(self, version):
        """Create item with given values, return ID of new version

        Args:
            version (wysteria.domain.Version): input version

        Returns:
            str, int

        Raises:
            Exception on network / server error
        """
        pass
    
    @abc.abstractmethod
    def create_resource(self, resource):
        """Create item with given values, return ID of new resource

        Args:
            resource (wysteria.domain.Resource): input resource

        Returns:
            str

        Raises:
            Exception on network / server error
        """
        pass
    
    @abc.abstractmethod
    def create_link(self, link):
        """Create item with given values, return ID of new link

        Args:
            link (wysteria.domain.Link): input link

        Returns:
            str

        Raises:
            Exception on network / server error
        """
        pass

    @abc.abstractmethod
    def delete_collection(self, oid):
        """Delete the matching obj type with the given id

        Args:
            oid (str): id of obj to delete

        Raises:
            Exception if deletion fails / network error
        """
        pass

    @abc.abstractmethod
    def delete_item(self, oid):
        """Delete the matching obj type with the given id

        (Links will be deleted automatically)

        Args:
            oid (str): id of obj to delete

        Raises:
            Exception if deletion fails / network error
        """
        pass

    @abc.abstractmethod
    def delete_version(self, oid):
        """Delete the matching obj type with the given id

        (Links will be deleted automatically)

        Args:
            oid (str): id of obj to delete

        Raises:
            Exception if deletion fails / network error
        """
        pass

    @abc.abstractmethod
    def delete_resource(self, oid):
        """Delete the matching obj type with the given id

        Args:
            oid (str): id of obj to delete

        Raises:
            Exception if deletion fails / network error
        """
        pass
