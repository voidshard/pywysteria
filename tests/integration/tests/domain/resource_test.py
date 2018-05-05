import pytest
import uuid

import wysteria


def _rs() -> str:
    """Create and return some string at random

    Returns:
        str
    """
    return uuid.uuid4().hex


class TestResource:
    """Tests for the Resource class"""

    @classmethod
    def setup_class(cls):
        cls.client = wysteria.Client()
        cls.client.connect()
        cls.collection = cls.client.create_collection(_rs())
        cls.item = cls.collection.create_item(_rs(), _rs())
        cls.version = cls.item.create_version()

    @classmethod
    def teardown_class(cls):
        cls.client.close()

    def _single_resource(self, id_):
        """Return a single resource by it's id

        Args:
            id_:

        Returns:
            Resource
        """
        s = self.client.search()
        s.params(id=id_)
        results = s.find_resources(limit=1)
        assert results
        return results[0]

    def test_create_resource_raises_on_duplicate(self):
        # arrange
        args = (_rs(), _rs(), _rs())
        self.version.add_resource(*args)

        # act & assert
        with pytest.raises(wysteria.errors.AlreadyExistsError):
            self.version.add_resource(*args)

    def test_create_resource_doesnt_raise_on_same_resource_different_version(self):
        # arrange
        args = (_rs(), _rs(), _rs())
        other_version = self.item.create_version()

        self.version.add_resource(*args)

        # act
        other_version.add_resource(*args)

        # assert
        assert True

    def test_delete_resource(self):
        # arrange
        resource = self.version.add_resource(_rs(), _rs(), _rs())

        s = self.client.search()
        s.params(id=resource.id)

        # act
        resource.delete()
        results = s.find_resources(limit=1)

        # assert
        assert not results

    def test_update_facets(self):
        # arrange
        facets = {
            _rs(): _rs(),
            _rs(): _rs(),
            _rs(): _rs(),
            _rs(): _rs(),
        }
        resource = self.version.add_resource(_rs(), _rs(), _rs())

        # act
        resource.update_facets(**facets)
        remote = self._single_resource(resource.id)

        # assert
        assert resource
        assert remote
        assert remote == resource
        for k, v in facets.items():
            assert resource.facets[k] == v
            assert remote.facets[k] == v

    def test_create_resource(self):
        # arrange
        name = _rs()
        type_ = _rs()
        location = _rs()
        facets = {
            _rs(): _rs(),
            _rs(): _rs(),
            _rs(): _rs(),
            _rs(): _rs(),
        }

        # act
        resource = self.version.add_resource(name, type_, location, facets=facets)
        remote = self._single_resource(resource.id)

        # assert
        assert resource
        assert remote
        assert remote == resource
        assert name == remote.name == resource.name
        assert location == remote.location == resource.location
        assert type_ == remote.resource_type == resource.resource_type
        assert resource.id
        assert resource.uri
        assert remote.id
        assert remote.uri
        for k, v in facets.items():
            assert resource.facets[k] == v
            assert remote.facets[k] == v
