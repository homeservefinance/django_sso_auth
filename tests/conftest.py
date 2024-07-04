import pytest
from django.contrib.auth import get_user_model
import logging


def pytest_configure(config):
    logging.basicConfig(level=logging.DEBUG)


username = "test_admin"
password = "test_admin"
email = "test_email@localhost"

User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    This fixture enables database access for all tests.
    """
    pass


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        User.objects.create(username=username, password=password, email=email)


@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
    }


@pytest.fixture
def okta_token(user_data):
    return {
        "userinfo": {
            "preferred_username": user_data["username"],
            "email": user_data["email"],
        }
    }
