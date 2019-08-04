import grpc
import json

from google.protobuf.struct_pb2 import Struct

from wysteria import domain
from wysteria.middleware.abstract_middleware import WysteriaConnectionBase
from wysteria.middleware.wgrpc import stubs
from wysteria.middleware.wgrpc.wysteria import grpc_pb2 as pb


_DEFAULT_URI = ":31000"  # default localhost, grpc port
_DEFAULT_LIMIT = 500


def _get_secure_channel(url, tls):
    """Return secure channel to server.

    Stolen from: https://www.programcreek.com/python/example/95418/grpc.secure_channel

    Args:
        url: host/port info of server
        tls: namedtuple of tls settings

    Returns:
        grpc.Channel

    Raises:
        IOError
        SSLError

    """
    credentials = grpc.ssl_channel_credentials(open(tls.cert).read())

    # create channel using ssl credentials
    return grpc.secure_channel(
        url, credentials, options=(
            ('grpc.ssl_target_name_override', "ABCD",),
        )
    )


def _handle_rpc_error(func):
    def fn(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except grpc.RpcError as e:
            error_data = json.loads(e.debug_error_string())
            WysteriaConnectionBase.translate_server_exception(
                error_data.get("grpc_message", str(e))
            )
    return fn


class GRPCMiddleware(WysteriaConnectionBase):
    """Wysteria middleware client using gRPC to manage transport.

    """
    def __init__(self, url, tls=None):
        self._url = url
        self._tls = tls
        self._channel = None
        self._stub = None

    def connect(self):
        """Connect to the other end.

        """
        if self._tls:
            if self._tls.enable:
                self._channel = grpc.secure_channel(self._url, self._tls)
            else:
                self._channel = grpc.insecure_channel(self._url)
        else:
            self._channel = grpc.insecure_channel(self._url)

        self._stub = stubs.WysteriaGrpcStub(self._channel)

    def close(self):
        self._channel.close()

    @_handle_rpc_error
    def _generic_find(self, query, limit, offset, finder, decoder):
        """Perform a generic wysteria query.

        Args:
            query: query object to encode
            limit: limit to apply
            offset: offset to apply
            finder: function to call & pass query to
            decoder: function to decode result objects

        Returns:
            list

        """
        reply = finder(
            pb.QueryDescs(
                Limit=limit,
                Offset=offset,
                all=[self._encode_query_desc(q) for q in query if q.is_valid]
            )
        )

        err = reply.error.Text
        if err:
            self.translate_server_exception(err)

        return [decoder(i) for i in reply.all]

    @_handle_rpc_error
    def _generic_create(self, obj, encoder, func):
        """

        Args:
            obj: obj to encode
            encoder: function to do the encoding
            func: function to call (create func)

        Returns:
            str

        """
        reply = func(encoder(obj))
        err = reply.error.Text
        if err:
            self.translate_server_exception(err)

        return reply.Id

    @_handle_rpc_error
    def _generic_update(self, oid, facets, func):
        """

        Args:
            oid: Id of obj to update
            facets: Facets to set
            func: Update function to call

        """
        result = func(pb.IdAndDict(Id=oid, Facets=facets))
        err = result.Text
        if err:
            self.translate_server_exception(err)

    @_handle_rpc_error
    def _generic_delete(self, oid, func):
        """Call remote delete.

        Args:
            oid: id of obj to delete
            func: delete function

        """
        result = func(pb.Id(Id=oid))

        err = result.Text
        if err:
            self.translate_server_exception(err)

    def find_collections(self, query, limit=_DEFAULT_LIMIT, offset=0):
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
        return self._generic_find(
            query,
            limit,
            offset,
            self._stub.FindCollections,
            self._decode_collection
        )

    def find_items(self, query, limit=_DEFAULT_LIMIT, offset=0):
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
        return self._generic_find(
            query,
            limit,
            offset,
            self._stub.FindItems,
            self._decode_item
        )

    def find_versions(self, query, limit=_DEFAULT_LIMIT, offset=0):
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
        return self._generic_find(
            query,
            limit,
            offset,
            self._stub.FindVersions,
            self._decode_version
        )

    def find_resources(self, query, limit=_DEFAULT_LIMIT, offset=0):
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
        return self._generic_find(
            query,
            limit,
            offset,
            self._stub.FindResources,
            self._decode_resource
        )

    def find_links(self, query, limit=_DEFAULT_LIMIT, offset=0):
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
        return self._generic_find(
            query,
            limit,
            offset,
            self._stub.FindLinks,
            self._decode_link
        )

    def get_published_version(self, oid):
        """Get the published version for the given Item id.

        Args:
            oid: id of parent Item

        Returns:
            Version

        """
        result = self._stub.PublishedVersion(pb.Id(Id=oid))

        err = result.error.Text
        if err:
            self.translate_server_exception(err)

        return self._decode_version(result)

    def publish_version(self, oid):
        """Publish the given version id.

        Args:
            oid: id of version to set as published

        """
        result = self._stub.SetPublishedVersion(pb.Id(Id=oid))

        err = result.Text
        if err:
            self.translate_server_exception(err)

    def update_collection_facets(self, oid, facets):
        """Update facets of a given Collection.

        Args:
            oid: id of object to update
            facets: dictionary of facets to set

        """
        self._generic_update(oid, facets, self._stub.UpdateCollectionFacets)

    def update_item_facets(self, oid, facets):
        """Update facets of a given Item.

        Args:
            oid: id of object to update
            facets: dictionary of facets to set

        """
        self._generic_update(oid, facets, self._stub.UpdateItemFacets)

    def update_version_facets(self, oid, facets):
        """Update facets of a given Version.

        Args:
            oid: id of object to update
            facets: dictionary of facets to set

        """
        self._generic_update(oid, facets, self._stub.UpdateVersionFacets)

    def update_resource_facets(self, oid, facets):
        """Update facets of a given Resource.

        Args:
            oid: id of object to update
            facets: dictionary of facets to set

        """
        self._generic_update(oid, facets, self._stub.UpdateResourceFacets)

    def update_link_facets(self, oid, facets):
        """Update facets of a given Link.

        Args:
            oid: id of object to update
            facets: dictionary of facets to set

        """
        self._generic_update(oid, facets, self._stub.UpdateLinkFacets)

    def create_collection(self, collection):
        """Create a Collection.

        Args:
            collection:

        Returns:
            str

        """
        return self._generic_create(
            collection, self._encode_collection, self._stub.CreateCollection
        )

    def create_item(self, item):
        """Create a Item.

        Args:
            item:

        Returns:
            str

        """
        return self._generic_create(
            item, self._encode_item, self._stub.CreateItem
        )

    def create_version(self, version):
        """Create a Version.

        Args:
            version:

        Returns:
            str, int

        """
        reply = self._stub.CreateVersion(self._encode_version(version))

        err = reply.Text
        if err:
            self.translate_server_exception(err)

        return reply.Id, reply.Version

    def create_resource(self, resource):
        """Create a Resource.

        Args:
            resource:

        Returns:
            str

        """
        return self._generic_create(
            resource, self._encode_resource, self._stub.CreateResource
        )

    def create_link(self, link):
        """Create a Link.

        Args:
            link:

        Returns:
            str

        """
        return self._generic_create(
            link, self._encode_link, self._stub.CreateLink
        )

    def delete_collection(self, oid):
        """Delete collection.

        Args:
            oid: id of obj to delete

        """
        self._generic_delete(oid, self._stub.DeleteCollection)

    def delete_item(self, oid):
        """Delete item.

        Args:
            oid: id of obj to delete

        """
        self._generic_delete(oid, self._stub.DeleteItem)

    def delete_version(self, oid):
        """Delete version.

        Args:
            oid: id of obj to delete

        """
        self._generic_delete(oid, self._stub.DeleteVersion)

    def delete_resource(self, oid):
        """Delete resource.

        Args:
            oid: id of obj to delete

        """
        self._generic_delete(oid, self._stub.DeleteResource)

    # -- Encoders
    def _encode_query_desc(self, q: domain.QueryDesc):
        """

        Args:
            q: domain.QueryDesc

        Returns:
            pb.QueryDesc
        """
        return pb.QueryDesc(
            Parent=q._parent,
            Id=q._id,
            Uri=q._uri,
            VersionNumber=q._versionnumber,
            ItemType=q._itemtype,
            Variant=q._variant,
            Facets=self._encode_dict(q._facets),
            Name=q._name,
            ResourceType=q._resourcetype,
            Location=q._location,
            LinkSrc=q._linksrc,
            LinkDst=q._linkdst,
        )

    def _encode_collection(self, o: domain.Collection):
        """

        Args:
            o: domain.Collection

        Returns:
            pb.Collection

        """
        return pb.Collection(
            Parent=o.parent,
            Id=o.id,
            Uri=o._uri,
            Name=o.name,
            Facets=self._encode_dict(o.facets),
        )

    def _encode_item(self, o: domain.Item):
        """

        Args:
            o: domain.Item

        Returns:
            pb.Item

        """
        return pb.Item(
            Parent=o.parent,
            Id=o.id,
            Uri=o._uri,
            ItemType=o.item_type,
            Variant=o.variant,
            Facets=self._encode_dict(o.facets),
        )

    def _encode_version(self, o: domain.Version):
        """

        Args:
            o: domain.version

        Returns:
            pb.version

        """
        return pb.Version(
            Parent=o.parent,
            Id=o.id,
            Uri=o._uri,
            Number=o._number,
            Facets=self._encode_dict(o.facets),
        )

    def _encode_resource(self, o: domain.Resource):
        """

        Args:
            o: domain.Resource

        Returns:
            pb.Resource

        """
        return pb.Resource(
            Parent=o.parent,
            Id=o.id,
            Uri=o._uri,
            Name=o.name,
            ResourceType=o.resource_type,
            Location=o.location,
            Facets=self._encode_dict(o.facets),
        )

    def _encode_link(self, o: domain.Link):
        """

        Args:
            o: domain.Link

        Returns:
            pb.Link

        """
        return pb.Link(
            Id=o.id,
            Uri=o._uri,
            Src=o.source,
            Dst=o.destination,
            Name=o.name,
            Facets=self._encode_dict(o.facets),
        )

    @staticmethod
    def _encode_dict(data: dict):
        s = Struct()
        for key, value in data.items():
            s.update({str(key): str(value)})
        return s

    # -- Decoders
    def _decode_collection(self, o: pb.Collection):
        """

        Args:
            o: pb.Collection

        Returns:
            domain.Collection

        """
        return domain.Collection(
            self,
            id=o.Id,
            uri=o.Uri,
            name=o.Name,
            parent=o.Parent,
            facets=dict(o.Facets or {}),
        )

    def _decode_item(self, o: pb.Item):
        """

        Args:
            o: pb.Item

        Returns:
            domain.Item

        """
        return domain.Item(
            self,
            id=o.Id,
            uri=o.Uri,
            parent=o.Parent,
            facets=dict(o.Facets or {}),
            itemtype=o.ItemType,
            variant=o.Variant,
        )

    def _decode_version(self, o: pb.Version):
        """

        Args:
            o: pb.Version

        Returns:
            domain.Version

        """
        return domain.Version(
            self,
            id=o.Id,
            uri=o.Uri,
            parent=o.Parent,
            facets=dict(o.Facets or {}),
            number=o.Number,
        )

    def _decode_resource(self, o: pb.Resource):
        """

        Args:
            o: pb.Resource

        Returns:
            domain.Resource

        """
        return domain.Resource(
            self,
            parent=o.Parent,
            name=o.Name,
            resourcetype=o.ResourceType,
            id=o.Id,
            uri=o.Uri,
            facets=dict(o.Facets or {}),
            location=o.Location,
        )

    def _decode_link(self, o: pb.Link):
        """

        Args:
            o: pb.Link

        Returns:
            domain.Link

        """
        return domain.Link(
            self,
            name=o.Name,
            id=o.Id,
            uri=o.Uri,
            facets=dict(o.Facets or {}),
            src=o.Src,
            dst=o.Dst,
        )


if __name__ == "__main__":
    from wysteria.utils import from_config

    def p(x):
        print(x.id, x.name, x.parent)

    c = from_config("/home/quintas/go/src/github.com/voidshard/pywysteria/wysteria-client.ini")
    c.connect()

    col = c.get_collection("foo")
    scol = c.get_collection("bar")

    print("\n", "all")
    for i in c.search().find_collections():
        p(i)

    print("\n", "children of v1", col.id)
    for i in c.search().params(parent=col.id).find_collections():
        p(i)

    print("\n", "children of v2", col.id)
    children = col.get_collections()
    for i in children:
        p(i)

    print("\n", "parent of", scol.id)
    p(scol.get_parent())

    c.close()
