import uuid

import wysteria


def _rs() -> str:
    """Create and return some string at random

    Returns:
        str
    """
    return uuid.uuid4().hex


class TestVersion:
    """Tests for the Version class"""

    @classmethod
    def setup_class(cls):
        cls.client = wysteria.Client()
        cls.client.connect()
        cls.collection = cls.client.create_collection(_rs())
        cls.item = cls.collection.create_item(_rs(), _rs())

    @classmethod
    def teardown_class(cls):
        cls.client.close()

    def test_delete_version(self):
        # arrange
        version = self.item.create_version()
        s = self.client.search()
        s.params(id=version.id)

        # act
        version.delete()
        remote = s.find_versions(limit=1)

        # assert
        assert not remote

    def test_resources_are_deleted_when_version_deleted(self):
        # arrange
        v = self.item.create_version()

        r1 = v.add_resource(_rs(), _rs(), _rs())
        r2 = v.add_resource(_rs(), _rs(), _rs())

        s = self.client.search()
        s.params(id=r1.id)
        s.params(id=r2.id)

        # act
        v.delete()

        results = s.find_resources(limit=3)

        # assert
        assert not results

    def test_link_versions(self):
        # arrange

        #  Desired link pattern
        #
        #        +---[foo]---> v2
        #  v1----|
        #        +---[foo]---> v3
        #
        #
        #  v(2/3) ----[bar]---> v1
        #
        v1 = self.item.create_version()
        v2 = self.item.create_version()
        v3 = self.item.create_version()

        # act
        v1_link_name = "foo"
        v1.link_to(v1_link_name, v2)
        v1.link_to(v1_link_name, v3)

        v23_link_name = "bar"
        v2.link_to(v23_link_name, v1)
        v3.link_to(v23_link_name, v1)

        # assert
        v1_linked = v1.get_linked()
        v2_linked = v2.get_linked()

        assert isinstance(v1_linked, dict)
        assert isinstance(v2_linked, dict)

        assert v1_link_name in v1_linked
        for l in v1_linked.get(v1_link_name, []):
            assert l in [v2, v3]

        assert v23_link_name in v2_linked
        assert v2_linked.get(v23_link_name, []) == [v1]

    def _single_version(self, id_):
        """Return a single version by Id

        Args:
            id_:

        Returns:
            Version
        """
        s = self.client.search()
        s.params(id=id_)
        result = s.find_versions(limit=1)
        assert result
        return result[0]

    def test_update_facets(self):
        # arrange
        facets = {
            _rs(): _rs(),
            _rs(): _rs(),
        }
        version = self.item.create_version()

        # act
        version.update_facets(**facets)
        remote = self._single_version(version.id)

        # assert
        assert version
        assert remote
        assert version == remote
        for k, v in facets.items():
            assert version.facets[k] == v
            assert remote.facets[k] == v

    def test_create_version_sets_facets(self):
        # arrange
        facets = {
            _rs(): _rs(),
            _rs(): _rs(),
        }

        # act
        version = self.item.create_version(facets)
        remote = self._single_version(version.id)

        # assert
        assert version
        assert remote
        assert version == remote
        for k, v in facets.items():
            assert version.facets[k] == v
            assert remote.facets[k] == v
