import pytest
import uuid

import wysteria


def _rs() -> str:
    """Create and return some string at random

    Returns:
        str
    """
    return uuid.uuid4().hex


class TestCollection:
    """Tests for the Collection class"""

    def _single_collection(self, id_):
        """Get a collection by it's id
        """
        search = self.client.search()
        search.params(id=id_)
        result = search.find_collections(limit=1)
        assert len(result) == 1
        return result[0]

    @classmethod
    def setup_class(cls):
        cls.client = wysteria.Client()
        cls.client.connect()

    @classmethod
    def teardown_class(cls):
        cls.client.close()

    def test_update_facets(self):
        # arrange
        expected = {"published_by": "batman", "foobar": "98172*(!@G*G&19832hOI&"}
        col = self.client.create_collection(_rs())

        # act
        col.update_facets(**expected)
        remote = self._single_collection(col.id)

        # assert
        for k, v in expected.items():
            assert col.facets[k] == v
            assert remote.facets[k] == v

    def test_create_child_collection(self):
        # arrange
        parent = self.client.create_collection(_rs())

        # act
        child = parent.create_collection(_rs())
        rparent = child.get_parent()
        rchildren = parent.get_collections()

        # assert
        assert child.parent == parent.id
        assert rparent == parent
        assert rchildren == [child]

    def test_delete_collection(self):
        # arrange
        col = self.client.create_collection(_rs())

        s = self.client.search()
        s.params(id=col.id)

        # act
        col.delete()

        result = s.find_collections(limit=2)

        # assert
        assert not result

    def test_find_collection_by_facets(self):
        # arrange
        facets = {
            "published_by": "zap",
        }

        expected = [
            self.client.create_collection(_rs(), facets=facets),
            self.client.create_collection(_rs(), facets=facets),
        ]

        not_expected = [
            self.client.create_collection(_rs()),
        ]

        s = self.client.search()
        s.params(facets=facets)

        # act
        result = s.find_collections(limit=10)

        # assert
        assert len(result) == len(expected)
        for r in result:
            assert r in expected
            assert r not in not_expected

    def test_find_collection_by_name(self):
        # arrange
        name1 = _rs()
        name2 = _rs()

        col1 = self.client.create_collection(name1)
        self.client.create_collection(name2)

        s = self.client.search()
        s.params(name=name1)

        # act
        result = s.find_collections(limit=2)

        # assert
        assert len(result) == 1
        assert result[0] == col1

    def test_find_collection_by_id(self):
        # arrange
        name = _rs()
        col = self.client.create_collection(name)
        s = self.client.search()
        s.params(id=col.id)

        # act
        result = s.find_collections(limit=2)

        # assert
        assert len(result) == 1
        assert result[0] == col

    def test_create_collection_raises_on_duplicate(self):
        # arrange
        name = _rs()
        self.client.create_collection(name)

        # act & assert
        with pytest.raises(wysteria.errors.AlreadyExistsError):
            self.client.create_collection(name)

    def test_create_collection_creates_remote_collection(self):
        # arrange
        name = _rs()
        facets = {"foo": "bar"}

        # act
        lresult = self.client.create_collection(name, facets=facets)
        rresult = self._single_collection(lresult.id)

        # assert
        for r in [lresult, rresult]:
            assert r
            assert r.name == name
            assert r.id
            assert r.facets

        assert rresult == lresult
        for k, v in facets.items():
            assert rresult.facets[k] == v
            assert lresult.facets[k] == v

