
import pytest
from django.contrib.auth import get_user_model
from django_sso_auth.drf.authentication import OktaJWTAuthentication


@pytest.fixture
def okta_jwt_authentication():
    return OktaJWTAuthentication()


@pytest.fixture
def mock_verify_token(mocker):
    return mocker.patch(
        "django_sso_auth.drf.authentication.OktaJWTAuthentication.verify_token_with_okta"
    )


def test_user_creation(okta_jwt_authentication, mock_verify_token):
    mock_verify_token.return_value = {
        "ver": 1,
        "jti": "AT.Y0pUZ32TLlvI8m4d8wD8T_5mkgS-OF01k6XEN2-rh_4",
        "iss": "https://homeservefinance.okta.com/oauth2/default",
        "aud": "api://default",
        "iat": 1720536165,
        "exp": 1720539765,
        "cid": "0oaepz8u5ple5hwgJ417",
        "uid": "00ud5tt8ykg39HdWE417",
        "scp": ["openid", "email", "profile"],
        "auth_time": 1720520213,
        "sub": "test@example.com",
    }
    User = get_user_model()
    assert User.objects.count() == 1
    okta_jwt_authentication.authenticate_credentials("token")
    assert User.objects.count() == 2
    user = User.objects.last()
    assert user.username == "test@example.com"
