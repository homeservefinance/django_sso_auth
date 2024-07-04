from unittest.mock import Mock


class MockOAuth:
    def __init__(self):
        self.registered_clients = {}

    def register(self, name, **kwargs):
        mock_client = Mock()
        mock_client.server_metadata = {"jwks_uri": "https://example.com/jwks"}
        mock_client.load_server_metadata = Mock()
        self.registered_clients[name] = mock_client
        return mock_client


oauth_mock = MockOAuth()
