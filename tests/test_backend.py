import pytest
from django.contrib.auth import get_user_model
from django_sso_auth.admin.backend import OktaBackend

User = get_user_model()


@pytest.mark.django_db
def test_authenticate_creates_user(okta_token, user_data):
    backend = OktaBackend()
    request = None  # Assuming request is not used in this case

    user = backend.authenticate(request, token=okta_token)

    assert user is not None
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]

    # Verify user is created in the database
    assert User.objects.filter(username=user_data["username"]).exists()


@pytest.mark.django_db
def test_authenticate_existing_user(okta_token, user_data):
    User.objects.create(username=user_data["username"], email=user_data["email"])

    backend = OktaBackend()
    request = None  # Assuming request is not used in this case

    user = backend.authenticate(request, token=okta_token)

    assert user is not None
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]

    # Ensure no duplicate user is created
    assert User.objects.filter(username=user_data["username"]).count() == 1


@pytest.mark.django_db
def test_get_user(user_data):
    user = User.objects.create(username=user_data["username"], email=user_data["email"])

    backend = OktaBackend()
    fetched_user = backend.get_user(user.id)

    assert fetched_user == user


@pytest.mark.django_db
def test_get_user_nonexistent():
    backend = OktaBackend()
    fetched_user = backend.get_user(99999)  # Assuming this ID doesn't exist

    assert fetched_user is None
