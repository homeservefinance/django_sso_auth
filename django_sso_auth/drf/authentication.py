from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

from django_sso_auth.utils import verify_token_with_okta

User = get_user_model()


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise AuthenticationFailed("Token missing or invalid")

        token = authorization.split(" ")[1]
        user = self.authenticate_credentials(token)
        if not user:
            raise AuthenticationFailed("Invalid token")
        return user, None

    def authenticate_credentials(self, token):
        try:
            user_info = verify_token_with_okta(token)
            user, _ = User.objects.get_or_create(
                username=user_info["sub"], defaults={"email": user_info["sub"]}
            )
            return user
        except User.DoesNotExist:
            raise AuthenticationFailed("No such user")
