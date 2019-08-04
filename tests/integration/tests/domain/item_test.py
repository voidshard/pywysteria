import pytest
import random
import uuid

import wysteria


def _rs() -> str:
    """Create and return some string at random

    Returns:
        str
    """
    return uuid.uuid4().hex


class TestItem:
    """Tests for the item class"""

    @classmethod
    def setup_class(cls):
        cls.client = wysteria.default_client()
        cls.client.connect()
        cls.collection = cls.client.create_collection(_rs())

    @classmethod
    def teardown_class(cls):
        cls.client.close()

    def test_create_version_itterates_versions_by_item(self):
        """Each item has it's own highest version number"""
        # arrange
        item1 = self.collection.create_item(_rs(), _rs())
        item2 = self.collection.create_item(_rs(), _rs())
        item1_version_numbers = [1, 2, 3]
        item2_version_numbers = [1, 2]

        # act
        versions1 = [
            item1.create_version(),
            item1.create_version(),
            item1.create_version(),
        ]
        versions2 = [
            item2.create_version(),
            item2.create_version(),
        ]

        # assert
        assert item1_version_numbers == [v.version for v in versions1]
        assert item2_version_numbers == [v.version for v in versions2]

        for v in versions1:
            assert v not in versions2
        for v in versions2:
            assert v not in versions1

    def test_publish_version_sets_given_version_as_published(self):
        """Regardless of what version is published, get_published() should return it.

        That is, it's perfectly acceptable to have versions 1-100, but have version 5 as
        the published one.
        """
        # arrange
        item = self.collection.create_item(_rs(), _rs())
        versions = [
            item.create_version(),
            item.create_version(),
            item.create_version(),
            item.create_version(),
            item.create_version(),
            item.create_version(),
            item.create_version(),
            item.create_version(),
            item.create_version(),
            item.create_version(),
            item.create_version(),
        ]

        for i in range(0, 20):
            pver = random.choice(versions)

            # act
            pver.publish()

            # assert
            result = item.get_published()
            assert result == pver

    def test_update_facets(self):
        # arrange
        facets = {
            _rs(): _rs(),
            _rs(): _rs(),
        }
        item = self.collection.create_item(_rs(), _rs())

        # act
        item.update_facets(**facets)
        remote = self.client.get_item(item.id)

        # assert
        for k, v in facets.items():
            assert item.facets[k] == v
            assert remote.facets[k] == v

    def test_create_version_itterates_versions(self):
        # arrange
        facets = {
            _rs(): _rs(),
            _rs(): _rs(),
        }
        item = self.collection.create_item(_rs(), _rs())
        expect_version_numbers = [1, 2, 3, 4, 5]

        # act
        versions = [
            item.create_version(facets),
            item.create_version(facets),
            item.create_version(facets),
            item.create_version(facets),
            item.create_version(facets),
        ]

        numbers = [v.version for v in versions]

        # assert
        assert numbers == expect_version_numbers
        for ver in versions:
            assert ver.parent == item.id
            for k, v in facets.items():
                assert ver.facets[k] == v

    def test_duplicate_item_different_parent_doesnt_raise(self):
        # arrange
        type_ = _rs()
        variant = _rs()

        self.collection.create_item(type_, variant)
        another_collection = self.client.create_collection(_rs())

        # act
        another_collection.create_item(type_, variant)

        # assert
        assert True

    def test_duplicate_item_raises(self):
        # arrange
        type_ = _rs()
        variant = _rs()

        self.collection.create_item(type_, variant)

        # act & assert
        with pytest.raises(wysteria.errors.AlreadyExistsError):
            self.collection.create_item(type_, variant)

    def test_link_items(self):
        # arrange
        self.collection.create_item(_rs(), _rs())

        #  Desired link pattern
        #
        #           +---[foo]---> item2
        #  item1----|
        #           +---[foo]---> item2
        #
        #
        #  item(2/3) ----[bar]---> item1
        #
        item1 = self.collection.create_item(_rs(), _rs())
        item2 = self.collection.create_item(_rs(), _rs())
        item3 = self.collection.create_item(_rs(), _rs())

        # act
        item1_link_name = "foo"
        item1.link_to(item1_link_name, item2)
        item1.link_to(item1_link_name, item3)

        item23_link_name = "bar"
        item2.link_to(item23_link_name, item1)
        item3.link_to(item23_link_name, item1)

        # assert
        item1_linked = item1.get_linked()
        item2_linked = item2.get_linked()

        assert isinstance(item1_linked, dict)
        assert isinstance(item2_linked, dict)

        assert item1_link_name in item1_linked
        for l in item1_linked.get(item1_link_name, []):
            assert l in [item2, item3]

        assert item23_link_name in item2_linked
        assert item2_linked.get(item23_link_name, []) == [item1]

    def test_delete_item(self):
        # arrange
        item = self.collection.create_item(_rs(), _rs())

        # act
        item.delete()
        remote = self.client.get_item(item.id)

        # assert
        assert not remote

    def test_find_item_by_facets(self):
        # arrange
        facets = {"fofofofooitems": _rs()}
        expected = [
            self.collection.create_item(_rs(), _rs(), facets=facets),
            self.collection.create_item(_rs(), _rs(), facets=facets),
        ]
        not_expected = [self.collection.create_item(_rs(), _rs())]

        s = self.client.search()
        s.params(facets=facets)

        # act
        results = s.find_items(limit=10)

        # assert
        assert len(results) == len(expected)
        for r in results:
            assert r in expected
            assert r not in not_expected

    def test_find_item_by_variant(self):
        # arrange
        variant = _rs()
        expected =[
            self.collection.create_item(_rs(), variant),
            self.collection.create_item(_rs(), variant),
        ]
        not_expected = [self.collection.create_item(_rs(), _rs())]

        s = self.client.search()
        s.params(item_variant=variant)

        # act
        results = s.find_items(limit=10)

        # assert
        assert len(results) == len(expected)
        for r in results:
            assert r in expected
            assert r not in not_expected

    def test_find_item_by_type(self):
        # arrange
        type_ = _rs()
        expected =[
            self.collection.create_item(type_, _rs()),
            self.collection.create_item(type_, _rs()),
        ]
        not_expected = [self.collection.create_item(_rs(), _rs())]

        s = self.client.search()
        s.params(item_type=type_)

        # act
        results = s.find_items(limit=10)

        # assert
        assert len(results) == len(expected)
        for r in results:
            assert r in expected
            assert r not in not_expected

    def test_create_item(self):
        # arrange
        facets = {
            "awesomefoo": _rs(),
            "awesomebar": _rs(),
        }

        # act
        item = self.collection.create_item(_rs(), _rs(), facets=facets)
        ritem = self.client.get_item(item.id)

        # assert
        assert item
        assert ritem
        assert item == ritem
        assert item.id
        assert ritem.id
        assert item.uri
        assert ritem.uri
        for k, v in facets.items():
            assert item.facets[k] == v
            assert ritem.facets[k] == v
