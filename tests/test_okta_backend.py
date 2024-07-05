import pytest
from django.contrib.auth import get_user_model
from django_sso_auth.admin.backend import OktaBackend

User = get_user_model()


@pytest.fixture
def okta_backend():
    return OktaBackend()


@pytest.fixture
def mock_user_model(mocker):
    return mocker.patch("django_sso_auth.admin.backend.User")


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("django_sso_auth.admin.backend.logger")


def test_authenticate_no_token(okta_backend, mock_logger):
    result = okta_backend.authenticate(None)
    assert result is None
    mock_logger.error.assert_called_with("No token provided for authentication")


def test_authenticate_no_username(okta_backend, mock_logger):
    token = {"userinfo": {"email": "test@example.com"}}
    result = okta_backend.authenticate(None, token)
    assert result is None
    mock_logger.error.assert_called_with("Username not found in token")


def test_authenticate_create_user(okta_backend, mock_user_model, mock_logger):
    token = {
        "userinfo": {"preferred_username": "testuser", "email": "test@example.com"}
    }
    mock_user_model.objects.get_or_create.return_value = (
        User(username="testuser"),
        True,
    )
    result = okta_backend.authenticate(None, token)
    assert result.username == "testuser"
    mock_logger.info.assert_called_with("Created new user: testuser")


def test_authenticate_existing_user(okta_backend, mock_user_model, mock_logger):
    token = {
        "userinfo": {
            "preferred_username": "existinguser",
            "email": "existing@example.com",
        }
    }
    mock_user_model.objects.get_or_create.return_value = (
        User(username="existinguser"),
        False,
    )
    result = okta_backend.authenticate(None, token)
    assert result.username == "existinguser"
    mock_logger.info.assert_not_called()


def test_authenticate_exception_handling(okta_backend, mock_user_model, mock_logger):
    token = {
        "userinfo": {"preferred_username": "testuser", "email": "test@example.com"}
    }
    mock_user_model.objects.get_or_create.side_effect = Exception("DB error")
    result = okta_backend.authenticate(None, token)
    assert result is None
    mock_logger.error.assert_called_with("Error in authentication process: DB error")


def test_get_user_existing(okta_backend, mock_user_model):
    mock_user_model.objects.get.return_value = User(username="testuser")
    result = okta_backend.get_user(1)
    assert result.username == "testuser"


def test_get_user_non_existing(okta_backend, mock_user_model, mock_logger):
    # Mock User.DoesNotExist to properly inherit from BaseException
    class MockDoesNotExist(Exception):
        pass

    mock_user_model.DoesNotExist = MockDoesNotExist
    mock_user_model.objects.get.side_effect = MockDoesNotExist
    result = okta_backend.get_user(1)
    assert result is None
    mock_logger.warning.assert_called_with("User with id 1 does not exist")
