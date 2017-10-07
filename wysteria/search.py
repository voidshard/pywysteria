from wysteria.domain import QueryDesc
from wysteria.constants import DEFAULT_QUERY_LIMIT


class Search(object):
    def __init__(self, conn):
        self._conn = conn
        self._query = []

    def params(self,
               id="",
               name="",
               parent="",
               version_number=0,
               item_type="",
               item_variant="",
               facets=None,
               resource_type="",
               resource_location="",
               link_source="",
               link_destination=""):
        """Append the given query description to the query we're going to
        launch. Objects returned will be required to match all of the terms
        specified on at least one of the query description objects.

        That is, the terms on each individual QueryDesc obj are considered "AND"
        and each QueryDesc in a list of QueryDesc objs are considered "OR" when
        taken together.

        Args:
            id (str):
            name (str):
            parent (str):
            version_number (int):
            item_type (str):
            item_variant (str):
            facets (dict):
            resource_type (str):
            resource_location (str):
            link_source (str):
            link_destination (str):

        Returns:
            bool
        """
        qd = QueryDesc()\
            .id(id)\
            .name(name)\
            .parent(parent)\
            .version_number(version_number)\
            .item_type(item_type)\
            .item_variant(item_variant)\
            .has_facets(facets)\
            .resource_type(resource_type)\
            .resource_location(resource_location)\
            .link_source(link_source)\
            .link_destination(link_destination)

        self._query.append(qd)

    def _generic_run_query(self, find_func, limit, offset):
        """Run the built query and return matching collections

        Returns:
            []domain.?

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return find_func(self._query, limit=limit, offset=offset)

    def find_collections(self, limit=DEFAULT_QUERY_LIMIT, offset=0):
        """Run the built query and return matching collections

        Args:
            limit (int): limit returned results
            offset (int): return results starting from offset

        Returns:
            []domain.Collection

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return self._generic_run_query(
            self._conn.find_collections, limit, offset
        )

    def find_items(self, limit=DEFAULT_QUERY_LIMIT, offset=0):
        """Run the built query and return matching items

        Args:
            limit (int): limit returned results
            offset (int): return results starting from offset

        Returns:
            []domain.Item

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return self._generic_run_query(self._conn.find_items, limit, offset)

    def find_versions(self, limit=DEFAULT_QUERY_LIMIT, offset=0):
        """Run the built query and return matching versions

        Args:
            limit (int): limit returned results
            offset (int): return results starting from offset

        Returns:
            []domain.Version

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return self._generic_run_query(self._conn.find_versions, limit, offset)

    def find_resources(self, limit=DEFAULT_QUERY_LIMIT, offset=0):
        """Run the built query and return matching resources

        Args:
            limit (int): limit returned results
            offset (int): return results starting from offset

        Returns:
            []domain.Resource

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return self._generic_run_query(self._conn.find_resources, limit, offset)

    def find_links(self, limit=DEFAULT_QUERY_LIMIT, offset=0):
        """Run the built query and return matching links

        Args:
            limit (int): limit returned results
            offset (int): return results starting from offset

        Returns:
            []domain.Link

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return self._generic_run_query(self._conn.find_links, limit, offset)
