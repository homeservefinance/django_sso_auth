import pytest
from django.contrib.auth import get_user_model
from django_sso_auth.admin.backend import OktaBackend
from faker import Faker

from tests.mocks.oauth import oauth_mock

fake = Faker()

User = get_user_model()


@pytest.fixture(autouse=True)
def mock_oauth(monkeypatch):
    monkeypatch.setattr("authlib.integrations.django_client.OAuth", oauth_mock)


@pytest.fixture
def token():
    return {
        "userinfo": {
            "sub": fake.uuid4(),
            "preferred_username": fake.email(),
            "email": fake.email(),
        }
    }


@pytest.fixture(autouse=True)
def mock_settings(settings):
    settings.SSO_AUTH = {
        "AUTH_API_CLIENT_ID": "test_client_id",
        "AUTH_ADMIN_CLIENT_ID": "test_admin_client_id",
        "AUTH_API_CLIENT_SECRET": "test_client_secret",
        "AUTH_DOMAIN": "test_domain",
    }


@pytest.fixture(autouse=True)
def mock_initialize_oauth_clients(monkeypatch):
    def mock_register_okta_api_client(self):
        return oauth_mock.register("okta_api")

    def mock_register_okta_admin_client(self):
        return oauth_mock.register("okta_admin")

    def mock_load_okta_api_metadata(self):
        self.okta_api_client.server_metadata = {"jwks_uri": "https://example.com/jwks"}
        self.okta_api_jwks_url = "https://example.com/jwks"

    monkeypatch.setattr(
        "django_sso_auth.conf.settings.SSOAuthSettings._register_okta_api_client",
        mock_register_okta_api_client,
    )
    monkeypatch.setattr(
        "django_sso_auth.conf.settings.SSOAuthSettings._register_okta_admin_client",
        mock_register_okta_admin_client,
    )
    monkeypatch.setattr(
        "django_sso_auth.conf.settings.SSOAuthSettings.load_okta_api_metadata",
        mock_load_okta_api_metadata,
    )


@pytest.mark.django_db
def test_authenticate_existing_user(token):
    user = User.objects.create(
        username=token["userinfo"]["preferred_username"],
        email=token["userinfo"]["email"],
        is_active=True,
    )
    backend = OktaBackend()
    authenticated_user = backend.authenticate(None, token=token)
    assert authenticated_user == user


@pytest.mark.django_db
def test_authenticate_new_user(token):
    backend = OktaBackend()
    authenticated_user = backend.authenticate(None, token=token)
    assert authenticated_user is not None
    assert authenticated_user.username == token["userinfo"]["preferred_username"]
    assert authenticated_user.email == token["userinfo"]["email"]
    assert authenticated_user.is_active


@pytest.mark.django_db
def test_authenticate_unauthorized_user(token):
    backend = OktaBackend()
    authenticated_user = backend.authenticate(None, token=token)
    assert authenticated_user is not None
