from rest_framework.exceptions import AuthenticationFailed
import jwt
from jwt import PyJWKClient
from django_sso_auth.conf import sso_settings


def verify_token_with_okta(token):
    try:
        client = sso_settings.OAUTH.okta_api
        if not client.server_metadata:
            client.load_server_metadata()

        jwks_url = client.server_metadata.get("jwks_uri")
        if not jwks_url:
            raise ValueError("JWKS URL not found in server metadata")

        jwk_client = PyJWKClient(jwks_url)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        audience = "api://default"
        issuer = client.server_metadata.get("issuer")
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
        )
        return claims
    except Exception as e:
        print(f"Exception details: {e}")
        raise AuthenticationFailed(f"Failed to verify token: {str(e)}")
