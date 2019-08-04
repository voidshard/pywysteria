import pytest
import uuid

import wysteria


def _rs() -> str:
    """Create and return some string at random

    Returns:
        str
    """
    return uuid.uuid4().hex


class TestLink:
    """Tests for the Link class"""

    @classmethod
    def setup_class(cls):
        cls.client = wysteria.default_client()
        cls.client.connect()
        cls.collection = cls.client.create_collection(_rs())
        cls.item1 = cls.collection.create_item(_rs(), _rs())
        cls.item2 = cls.collection.create_item(_rs(), _rs())
        cls.version1 = cls.item1.create_version()
        cls.version2 = cls.item2.create_version()

    @classmethod
    def teardown_class(cls):
        cls.client.close()

    def _single_link(self, id_):
        """Return a single link by Id

        Args:
            id_:

        Returns:
            Link
        """
        s = self.client.search()
        s.params(id=id_)
        results = s.find_links(limit=1)
        assert results
        return results[0]

    def test_links_are_deleted_when_version_is_deleted(self):
        # arrange
        v1 = self.item1.create_version()
        v2 = self.item2.create_version()

        l1 = v1.link_to(_rs(), v2)
        l2 = v2.link_to(_rs(), v1)

        s = self.client.search()
        s.params(id=l1.id)
        s.params(id=l2.id)

        # act
        v1.delete()

        results = s.find_links(limit=3)

        # assert
        assert not results

    def test_links_are_deleted_when_item_is_deleted(self):
        # arrange
        v1 = self.collection.create_item(_rs(), _rs())
        v2 = self.collection.create_item(_rs(), _rs())

        l1 = v1.link_to(_rs(), v2)
        l2 = v2.link_to(_rs(), v1)

        s = self.client.search()
        s.params(id=l1.id)
        s.params(id=l2.id)

        # act
        v1.delete()

        results = s.find_links(limit=3)

        # assert
        assert not results

    def test_raises_on_duplicate_item_link(self):
        # arrange
        name = _rs()
        self.item1.link_to(name, self.item2)

        # act & assert
        with pytest.raises(wysteria.errors.AlreadyExistsError):
            self.item1.link_to(name, self.item2)

    def test_raises_on_duplicate_version_link(self):
        # arrange
        name = _rs()
        self.version1.link_to(name, self.version2)

        # act & assert
        with pytest.raises(wysteria.errors.AlreadyExistsError):
            self.version1.link_to(name, self.version2)

    def test_raises_on_self_link_item(self):
        # arrange
        name = _rs()

        # act & assert
        with pytest.raises(wysteria.errors.IllegalOperationError):
            self.item1.link_to(name, self.item1)

    def test_raises_on_self_link_version(self):
        # arrange
        name = _rs()

        # act & assert
        with pytest.raises(wysteria.errors.IllegalOperationError):
            self.version1.link_to(name, self.version1)

    def test_raises_on_cross_object_link(self):
        # arrange
        name = _rs()

        # act & assert
        with pytest.raises(ValueError):
            self.version1.link_to(name, self.item1)

        with pytest.raises(ValueError):
            self.item1.link_to(name, self.version1)

    def test_update_facets_version_link(self):
        # arrange
        name = _rs()
        facets = {
            _rs(): _rs(),
            _rs(): _rs(),
            _rs(): _rs(),
        }
        lnk = self.version1.link_to(name, self.version2)

        # act
        lnk.update_facets(**facets)
        remote = self._single_link(lnk.id)

        # assert
        for k, v in facets.items():
            assert lnk.facets[k] == v
            assert remote.facets[k] == v

    def test_update_facets_item_link(self):
        # arrange
        name = _rs()
        facets = {
            _rs(): _rs(),
            _rs(): _rs(),
            _rs(): _rs(),
        }
        lnk = self.item1.link_to(name, self.item2)

        # act
        lnk.update_facets(**facets)
        remote = self._single_link(lnk.id)

        # assert
        for k, v in facets.items():
            assert lnk.facets[k] == v
            assert remote.facets[k] == v

    def test_create_version_link(self):
        # arrange
        name = _rs()
        facets = {
            _rs(): _rs(),
            _rs(): _rs(),
            _rs(): _rs(),
        }

        # act
        lnk = self.version1.link_to(name, self.version2, facets=facets)
        remote = self._single_link(lnk.id)

        # assert
        assert lnk
        assert remote
        assert lnk == remote
        assert lnk.destination == remote.destination == self.version2.id
        assert lnk.source == remote.source == self.version1.id
        for k, v in facets.items():
            assert lnk.facets[k] == v
            assert remote.facets[k] == v

    def test_create_item_link(self):
        # arrange
        name = _rs()
        facets = {
            _rs(): _rs(),
            _rs(): _rs(),
            _rs(): _rs(),
        }

        # act
        lnk = self.item1.link_to(name, self.item2, facets=facets)
        remote = self._single_link(lnk.id)

        # assert
        assert lnk
        assert remote
        assert lnk == remote
        assert lnk.destination == remote.destination == self.item2.id
        assert lnk.source == remote.source == self.item1.id
        assert lnk.id
        assert lnk.uri
        for k, v in facets.items():
            assert lnk.facets[k] == v
            assert remote.facets[k] == v
