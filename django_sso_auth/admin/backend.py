import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()
logger = logging.getLogger(__name__)


class OktaBackend(BaseBackend):
    def authenticate(self, request, token=None):
        if token is None:
            logger.error("No token provided for authentication")
            return None

        try:
            # Extract user info from the token
            okta_user_info = token.get("userinfo", {})
            username = okta_user_info.get("preferred_username")
            email = okta_user_info.get("email", "")

            if not username:
                logger.error("Username not found in token")
                return None

            user, created = User.objects.get_or_create(
                username=username, defaults={"email": email, "is_active": True}
            )

            if created:
                logger.info(f"Created new user: {username}")

            # For testing purposes, let's consider all users as authorized
            # In a real scenario, you'd implement proper authorization checks here
            return user

        except Exception as e:
            logger.error(f"Error in authentication process: {e}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.warning(f"User with id {user_id} does not exist")
            return None
