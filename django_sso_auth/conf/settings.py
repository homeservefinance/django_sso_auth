from django.conf import settings
from authlib.integrations.django_client import OAuth


class SSOAuthSettings:
    def __init__(self):
        self.AUTH_API_CLIENT_ID = getattr(settings, "AUTH_API_CLIENT_ID", "")
        self.AUTH_ADMIN_CLIENT_ID = getattr(settings, "AUTH_ADMIN_CLIENT_ID", "")
        self.AUTH_API_CLIENT_SECRET = getattr(settings, "AUTH_API_CLIENT_SECRET", "")
        self.AUTH_DOMAIN = getattr(settings, "AUTH_DOMAIN", "")
        self.OAUTH = None

    def register_oauth(self):
        self.OAUTH = OAuth()
        self.OAUTH.register(
            "okta_api",
            client_id=self.AUTH_API_CLIENT_ID,
            client_kwargs={"scope": "openid profile email"},
            server_metadata_url=f"https://{self.AUTH_DOMAIN}/.well-known/openid-configuration",
        )
        self.OAUTH.register(
            "okta_admin",
            client_id=self.AUTH_ADMIN_CLIENT_ID,
            client_secret=self.AUTH_API_CLIENT_SECRET,
            client_kwargs={"scope": "openid profile email"},
            server_metadata_url=f"https://{self.AUTH_DOMAIN}/.well-known/openid-configuration",
        )
