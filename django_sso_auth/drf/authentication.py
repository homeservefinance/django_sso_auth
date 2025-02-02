import logging

from django.contrib.auth import get_user_model
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWKClient
from jwt import decode as jwt_decode
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django_sso_auth.conf import sso_auth_settings

logger = logging.getLogger(__name__)
User = get_user_model()


class OktaJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None

        token = authorization.split(" ")[1]
        try:
            user, user_info = self.authenticate_credentials(token)
        except AuthenticationFailed as e:
            # if we are used in a list of authentications we should return None
            # then django will try the next authentication method
            return None
        return user, user_info

    def authenticate_credentials(self, token):
        try:
            user_info = self.verify_token_with_okta(token)
            email = user_info.get("sub")
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    "email": email,
                    "is_active": True,
                    "is_staff": True,
                    "is_superuser": True,
                },
            )
            return user, user_info
        except Exception as e:
            raise AuthenticationFailed(f"Failed to authenticate: {str(e)}")

    @staticmethod
    def verify_token_with_okta(token):
        try:
            sso_auth_settings.load_okta_api_metadata()
            jwks_url = sso_auth_settings.okta_api_jwks_url
            jwk_client = PyJWKClient(jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            audience = "api://default"
            issuer = sso_auth_settings.okta_api_client.server_metadata.get("issuer")
            claims = jwt_decode(
                token,
                signing_key.key,
                algorithms=sso_auth_settings.AUTH_ALGORITHMS,
                audience=audience,
                issuer=issuer,
            )
            return claims
        except ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {str(e)}")
        except Exception as e:
            print(f"Exception details: {e}")
            raise AuthenticationFailed(f"Failed to verify token: {str(e)}")
