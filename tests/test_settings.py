# import pytest
# from unittest.mock import patch, MagicMock
# from django.conf import settings
# from django_sso_auth.conf.settings import SSOAuthSettings
#
# @pytest.fixture
# def mock_settings():
#     settings.AUTH_API_CLIENT_ID = "test_api_client_id"
#     settings.AUTH_ADMIN_CLIENT_ID = "test_admin_client_id"
#     settings.AUTH_API_CLIENT_SECRET = "test_client_secret"
#     settings.AUTH_DOMAIN = "test.okta.com"
#     yield
#     del settings.AUTH_API_CLIENT_ID
#     del settings.AUTH_ADMIN_CLIENT_ID
#     del settings.AUTH_API_CLIENT_SECRET
#     del settings.AUTH_DOMAIN
#
# @pytest.fixture
# def mock_oauth():
#     with patch("django_sso_auth.conf.settings.OAuth") as MockOAuth:
#         mock_instance = MockOAuth.return_value
#         mock_instance.register.return_value = MagicMock()
#         yield mock_instance
#
# @pytest.fixture
# def mock_load_server_metadata():
#     with patch("django_sso_auth.conf.settings.SSOAuthSettings._initialize_oauth_clients") as mock_method:
#         mock_method.return_value = None
#         yield mock_method
#
# @pytest.mark.usefixtures("mock_settings", "mock_load_server_metadata")
# def test_ssoauthsettings_initialization(mock_oauth):
#     sso_settings = SSOAuthSettings()
#
#     assert sso_settings.AUTH_API_CLIENT_ID == "test_api_client_id"
#     assert sso_settings.AUTH_ADMIN_CLIENT_ID == "test_admin_client_id"
#     assert sso_settings.AUTH_API_CLIENT_SECRET == "test_client_secret"
#     assert sso_settings.AUTH_DOMAIN == "test.okta.com"
#     assert sso_settings.AUTH_ALGORITHMS == ["RS256"]
#     assert sso_settings.OAUTH is not None
#     assert sso_settings.okta_api_client is not None
#     assert sso_settings.okta_admin_client is not None
#
#     mock_oauth.register.assert_any_call(
#         "okta_api",
#         client_id="test_api_client_id",
#         client_kwargs={"scope": "openid profile email"},
#         server_metadata_url="https://test.okta.com/.well-known/openid-configuration",
#     )
#     mock_oauth.register.assert_any_call(
#         "okta_admin",
#         client_id="test_admin_client_id",
#         client_secret="test_client_secret",
#         client_kwargs={"scope": "openid profile email"},
#         server_metadata_url="https://test.okta.com/.well-known/openid-configuration",
#     )
#
# @pytest.mark.usefixtures("mock_settings", "mock_load_server_metadata")
# def test_ssoauthsettings_missing_jwks_url(mock_oauth):
#     # Simulate missing jwks_uri in server metadata
#     mock_oauth.register.return_value.server_metadata = {}
#
#     with pytest.raises(ValueError, match="JWKS URL not found in server metadata"):
#         SSOAuthSettings()
