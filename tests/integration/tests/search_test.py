from copy import copy
import uuid

import wysteria


def _rs() -> str:
    """Create and return some string at random

    Returns:
        str
    """
    return uuid.uuid4().hex


class TestSearch:
    """Tests for the Search class"""

    @classmethod
    def setup_class(cls):
        cls.client = wysteria.Client()
        cls.client.connect()

        cls.common_facets = {
            _rs(): _rs(),
        }

        cls.collection1 = cls.client.create_collection(_rs(), facets=cls.common_facets)
        cls.collection2 = cls.client.create_collection(_rs(), facets=cls.common_facets)
        cls.item1 = cls.collection1.create_item(_rs(), _rs(), facets=cls.common_facets)
        cls.item2 = cls.collection2.create_item(_rs(), _rs(), facets=cls.common_facets)
        cls.version1 = cls.item1.create_version(facets=cls.common_facets)
        cls.version2 = cls.item2.create_version(facets=cls.common_facets)
        cls.link1 = cls.version1.link_to(_rs(), cls.version2, facets=cls.common_facets)
        cls.link2 = cls.item1.link_to(_rs(), cls.item2, facets=cls.common_facets)
        cls.resource1 = cls.version1.add_resource(_rs(), _rs(), _rs(), facets=cls.common_facets)
        cls.resource2 = cls.version2.add_resource(_rs(), _rs(), _rs(), facets=cls.common_facets)

    @classmethod
    def teardown_class(cls):
        cls.client.close()

    def test_search_pagination(self):
        # arrange
        item = self.collection1.create_item(_rs(), _rs())
        expected = [item.create_version() for _ in range(0, 100)]

        s = self.client.search()
        s.params(parent=item.id)

        limit = 10
        offset = 0
        found = limit + 1
        all_results = []

        # act & assert
        while found >= limit:
            results = s.find_versions(limit=limit, offset=offset)

            assert len(results) <= limit
            for r in results:
                assert r not in all_results

            offset += limit
            found = len(results)
            all_results.extend(results)

        assert len(expected) == len(all_results)
        for r in all_results:
            assert r in expected
        for r in expected:
            assert r in all_results

    def test_facet_search(self):
        # arrange
        s = self.client.search()
        s.params(facets=self.common_facets)

        expected = [
            (s.find_collections, [self.collection1, self.collection2]),
            (s.find_items, [self.item1, self.item2]),
            (s.find_versions, [self.version1, self.version2]),
            (s.find_resources, [self.resource1, self.resource2]),
            (s.find_links, [self.link1, self.link2]),
        ]

        for fn, expected_results in expected:
            # act
            results = fn(limit=10)

            # assert
            assert len(results) == len(expected_results)
            for r in results:
                assert r in expected_results

            for r in expected_results:
                assert r in results
