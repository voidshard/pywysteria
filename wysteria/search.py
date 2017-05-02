from wysteria.domain import QueryDesc


class Search(object):
    def __init__(self, conn):
        self._conn = conn
        self._query = []

    def params(self,
               id="",
               name="",
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
            .version_number(version_number)\
            .item_type(item_type)\
            .item_variant(item_variant)\
            .has_facets(facets)\
            .resource_type(resource_type)\
            .resource_location(resource_location)\
            .link_source(link_source)\
            .link_destination(link_destination)        
        
        if not qd.is_valid:
            return False

        self._query.append(qd)
        return True

    def _ready_search(self):
        """Returns if we are ready to launch query, that is we must have at
        least one valid query ready to go.

        Returns:
            bool
        """
        return len(self._query) > 0

    def _generic_run_query(self, find_func):
        """Run the built query and return matching collections

        Returns:
            []domain.?

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        if not self._ready_search():
            return []
        return find_func(self._query)

    def find_collections(self):
        """Run the built query and return matching collections

        Returns:
            []domain.Collection

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return self._generic_run_query(self._conn.find_collections)

    def find_items(self):
        """Run the built query and return matching items

        Returns:
            []domain.Item

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return self._generic_run_query(self._conn.find_items)

    def find_versions(self):
        """Run the built query and return matching versions

        Returns:
            []domain.Version

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return self._generic_run_query(self._conn.find_versions)

    def find_resources(self):
        """Run the built query and return matching resources

        Returns:
            []domain.Resource

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return self._generic_run_query(self._conn.find_resources)

    def find_links(self):
        """Run the built query and return matching links

        Returns:
            []domain.Link

        Raises:
            wysteria.errors.InvalidQuery if no search terms given
        """
        return self._generic_run_query(self._conn.find_links)
