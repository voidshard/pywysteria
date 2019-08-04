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

    @classmethod
    def setup_class(cls):
        cls.client = wysteria.default_client()
        cls.client.connect()

    @classmethod
    def teardown_class(cls):
        cls.client.close()

    def test_get_item_returns_desired_item(self):
        # arrange
        col = self.client.create_collection(_rs())
        item = col.create_item(_rs(), _rs())
        col.create_item(_rs(), _rs())

        # act
        result = self.client.get_item(item.id)

        # assert
        assert result == item

    def test_get_collection_returns_by_name_or_id(self):
        # arrange
        col = self.client.create_collection(_rs())
        self.client.create_collection(_rs())

        # act
        iresult = self.client.get_collection(col.id)
        nresult = self.client.get_collection(col.name)

        # assert
        assert col == iresult
        assert col == nresult
