# Where applicable, these facets are populated automatically by the client
FACET_COLLECTION = "collection"
FACET_ITEM_TYPE = "itemtype"
FACET_ITEM_VARIANT = "variant"
FACET_LINK_TYPE = "linktype"

# Where FACET_LINK_TYPE is used, the value will be one of these VALUE_LINK_TYPE_* vars
VALUE_LINK_TYPE_ITEM = "item"
VALUE_LINK_TYPE_VERSION = "version"

# A default for the 'limit' field send to wysteria on a search request.
DEFAULT_QUERY_LIMIT = 500

ERR_ALREADY_EXISTS = "already-exists"
ERR_INVALID = "invalid-input"
ERR_ILLEGAL = "illegal-operation"
ERR_NOT_FOUND = "not-found"
ERR_NOT_SERVING = "operation-rejected"
