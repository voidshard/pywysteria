import uuid

import wysteria


def _rs() -> str:
    """Create and return some string at random

    Returns:
        str
    """
    return uuid.uuid4().hex


class TestClient:
    """Tests for the client class"""

    def _single_collection(self, id_):
        """Get a collection by it's id
        """
        search = self.client.search()
        search.params(id=id_)
        result = search.find_collections(limit=1)
        if result:
            return result[0]
        return None

    @classmethod
    def setup_class(cls):
        cls.client = wysteria.Client()
        cls.client.connect()

    @classmethod
    def teardown_class(cls):
        cls.client.close()

    def test_create_collection_creates_remote_collection(self):
        # arrange
        name = _rs()

        # act
        lresult = self.client.create_collection(name)
        rresult = self._single_collection(lresult.id)

        # assert
        for r in [lresult, rresult]:
            assert r
            assert r.name == name
            assert r.id
            assert r.facets

        assert rresult == lresult
