from django.conf import settings
from authlib.integrations.django_client import OAuth


class SSOAuthSettings:
    def __init__(self):
        self.AUTH_API_CLIENT_ID = getattr(settings, "AUTH_API_CLIENT_ID", "")
        self.AUTH_ADMIN_CLIENT_ID = getattr(settings, "AUTH_ADMIN_CLIENT_ID", "")
        self.AUTH_API_CLIENT_SECRET = getattr(settings, "AUTH_API_CLIENT_SECRET", "")
        self.AUTH_DOMAIN = getattr(settings, "AUTH_DOMAIN", "")
        self.AUTH_ALGORITHMS = ["RS256"]
        self.OAUTH = None
        self.okta_api_client = None
        self.okta_admin_client = None
        self.okta_api_jwks_url = None
        self._initialize_oauth_clients()

    def _initialize_oauth_clients(self):
        self.OAUTH = OAuth()
        self.okta_api_client = self.OAUTH.register(
            "okta_api",
            client_id=self.AUTH_API_CLIENT_ID,
            client_kwargs={"scope": "openid profile email"},
            server_metadata_url=f"https://{self.AUTH_DOMAIN}/.well-known/openid-configuration",
        )
        self.okta_admin_client = self.OAUTH.register(
            "okta_admin",
            client_id=self.AUTH_ADMIN_CLIENT_ID,
            client_secret=self.AUTH_API_CLIENT_SECRET,
            client_kwargs={"scope": "openid profile email"},
            server_metadata_url=f"https://{self.AUTH_DOMAIN}/.well-known/openid-configuration",
        )

        # Load server metadata for okta_api_client
        if not self.okta_api_client.server_metadata:
            self.okta_api_client.load_server_metadata()

        self.okta_api_jwks_url = self.okta_api_client.server_metadata.get("jwks_uri")
        if not self.okta_api_jwks_url:
            raise ValueError("JWKS URL not found in server metadata")
