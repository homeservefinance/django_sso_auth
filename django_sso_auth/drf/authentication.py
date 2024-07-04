from rest_framework.authentication import BaseAuthentication
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
import jwt
from jwt import PyJWKClient, ExpiredSignatureError, InvalidTokenError
from django_sso_auth.conf import sso_auth_settings

User = get_user_model()


class OktaJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise AuthenticationFailed("Token missing or invalid")

        token = authorization.split(" ")[1]
        user, user_info = self.authenticate_credentials(token)
        if not user:
            raise AuthenticationFailed("Invalid token")
        return user, user_info

    def authenticate_credentials(self, token):
        try:
            user_info = self.verify_token_with_okta(token)
            print(f"User info: {user_info}")
            user, _ = User.objects.get_or_create(
                username=user_info["sub"], defaults={"email": user_info["sub"]}
            )
            return user, user_info
        except User.DoesNotExist:
            raise AuthenticationFailed("No such user")
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
            claims = jwt.decode(
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
