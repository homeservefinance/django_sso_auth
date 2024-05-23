from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class OktaBackend(BaseBackend):
    def authenticate(self, request, token=None):
        # Your logic to parse token and get user info
        print(f"Token: {token}")
        okta_user_info = token["userinfo"]
        username = okta_user_info["preferred_username"]
        email = okta_user_info.get("email", "")

        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        if created:
            # Set additional user fields if needed
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
