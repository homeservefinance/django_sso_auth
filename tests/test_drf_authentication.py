from unittest.mock import MagicMock, patch

import pytest
from django_sso_auth.drf.authentication import OktaJWTAuthentication
from jwt import ExpiredSignatureError, InvalidTokenError
from rest_framework.exceptions import AuthenticationFailed


@pytest.fixture
def okta_jwt_authentication():
    return OktaJWTAuthentication()


@pytest.fixture
def mock_user_model(mocker):
    return mocker.patch("django_sso_auth.drf.authentication.User")


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("django_sso_auth.drf.authentication.logger")


@pytest.fixture
def mock_sso_auth_settings(mocker):
    return mocker.patch("django_sso_auth.drf.authentication.sso_auth_settings")


@pytest.fixture
def mock_pyjwkclient(mocker):
    return mocker.patch("django_sso_auth.drf.authentication.PyJWKClient")


def test_authenticate_no_authorization_header(okta_jwt_authentication):
    request = MagicMock(headers={})
    with pytest.raises(AuthenticationFailed, match="Token missing or invalid"):
        okta_jwt_authentication.authenticate(request)


def test_authenticate_invalid_authorization_header(okta_jwt_authentication):
    request = MagicMock(headers={"Authorization": "InvalidToken"})
    with pytest.raises(AuthenticationFailed, match="Token missing or invalid"):
        okta_jwt_authentication.authenticate(request)


def test_authenticate_credentials_exception(okta_jwt_authentication, mock_user_model):
    token = "testtoken"
    request = MagicMock(headers={"Authorization": f"Bearer {token}"})
    with patch.object(
        OktaJWTAuthentication,
        "authenticate_credentials",
        side_effect=AuthenticationFailed("Invalid token"),
    ):
        with pytest.raises(AuthenticationFailed, match="Invalid token"):
            okta_jwt_authentication.authenticate(request)


def test_authenticate_credentials_success(okta_jwt_authentication, mock_user_model):
    token = "testtoken"
    request = MagicMock(headers={"Authorization": f"Bearer {token}"})
    user = mock_user_model(username="testuser")
    with patch.object(
        OktaJWTAuthentication,
        "authenticate_credentials",
        return_value=(user, {"sub": "testuser"}),
    ):
        result = okta_jwt_authentication.authenticate(request)
        assert result == (user, {"sub": "testuser"})


def test_authenticate_credentials_create_user(okta_jwt_authentication, mock_user_model):
    token = "testtoken"
    user_info = {"sub": "newuser", "email": "newuser@example.com"}
    with patch.object(
        OktaJWTAuthentication, "verify_token_with_okta", return_value=user_info
    ):
        mock_user = MagicMock()
        mock_user.username = "newuser"
        mock_user_model.objects.get_or_create.return_value = (mock_user, True)
        user, user_info_returned = okta_jwt_authentication.authenticate_credentials(
            token
        )
        assert user.username == "newuser"
        assert user_info_returned == user_info


def test_authenticate_credentials_existing_user(
    okta_jwt_authentication, mock_user_model
):
    token = "testtoken"
    user_info = {"sub": "existinguser", "email": "existing@example.com"}
    with patch.object(
        OktaJWTAuthentication, "verify_token_with_okta", return_value=user_info
    ):
        mock_user = MagicMock()
        mock_user.username = "existinguser"
        mock_user_model.objects.get_or_create.return_value = (mock_user, False)
        user, user_info_returned = okta_jwt_authentication.authenticate_credentials(
            token
        )
        assert user.username == "existinguser"
        assert user_info_returned == user_info


def test_verify_token_with_okta_success(
    okta_jwt_authentication, mock_sso_auth_settings, mock_pyjwkclient
):
    token = "testtoken"
    mock_sso_auth_settings.load_okta_api_metadata.return_value = None
    mock_sso_auth_settings.okta_api_jwks_url = (
        "https://example.com/.well-known/jwks.json"
    )
    mock_pyjwkclient_instance = mock_pyjwkclient.return_value
    mock_pyjwkclient_instance.get_signing_key_from_jwt.return_value.key = "testkey"
    mock_sso_auth_settings.AUTH_ALGORITHMS = ["RS256"]
    mock_sso_auth_settings.okta_api_client.server_metadata.get.return_value = (
        "https://issuer.example.com"
    )
    with patch(
        "django_sso_auth.drf.authentication.jwt_decode",
        return_value={"sub": "testuser"},
    ):
        claims = okta_jwt_authentication.verify_token_with_okta(token)
        assert claims == {"sub": "testuser"}


def test_verify_token_with_okta_expired(
    okta_jwt_authentication, mock_sso_auth_settings, mock_pyjwkclient
):
    token = "testtoken"
    mock_sso_auth_settings.load_okta_api_metadata.return_value = None
    mock_sso_auth_settings.okta_api_jwks_url = (
        "https://example.com/.well-known/jwks.json"
    )
    mock_pyjwkclient_instance = mock_pyjwkclient.return_value
    mock_pyjwkclient_instance.get_signing_key_from_jwt.return_value.key = "testkey"

    with patch(
        "django_sso_auth.drf.authentication.jwt_decode",
        side_effect=ExpiredSignatureError,
    ):
        with pytest.raises(AuthenticationFailed, match="Token has expired"):
            okta_jwt_authentication.verify_token_with_okta(token)


def test_verify_token_with_okta_invalid(
    okta_jwt_authentication, mock_sso_auth_settings
):
    token = "testtoken"
    mock_sso_auth_settings.load_okta_api_metadata.return_value = None
    mock_sso_auth_settings.okta_api_jwks_url = (
        "https://example.com/.well-known/jwks.json"
    )
    with patch(
        "django_sso_auth.drf.authentication.jwt_decode", side_effect=InvalidTokenError
    ):
        with pytest.raises(AuthenticationFailed, match="Invalid token"):
            okta_jwt_authentication.verify_token_with_okta(token)


def test_verify_token_with_okta_generic_exception(
    okta_jwt_authentication, mock_sso_auth_settings, mock_pyjwkclient
):
    token = "testtoken"
    mock_sso_auth_settings.load_okta_api_metadata.return_value = None
    mock_sso_auth_settings.okta_api_jwks_url = (
        "https://example.com/.well-known/jwks.json"
    )
    mock_pyjwkclient_instance = mock_pyjwkclient.return_value
    mock_pyjwkclient_instance.get_signing_key_from_jwt.side_effect = Exception(
        "Generic error"
    )
    with pytest.raises(
        AuthenticationFailed, match="Failed to verify token: Generic error"
    ):
        okta_jwt_authentication.verify_token_with_okta(token)
