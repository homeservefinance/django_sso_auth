from django.conf import settings
from django.utils.module_loading import import_string

USER_SETTINGS = getattr(settings, "SSO_AUTH", {})

DEFAULTS = {
    "AUTH_API_CLIENT_ID": "",
    "AUTH_ADMIN_CLIENT_ID": "",
    "AUTH_API_CLIENT_SECRET": "",
    "AUTH_DOMAIN": "",
    "AUTH_ALGORITHMS": ["RS256"],
    "OAUTH_CLASS": "authlib.integrations.django_client.OAuth",
}

IMPORT_STRINGS = ["OAUTH_CLASS"]


def perform_import(value, setting_name):
    if isinstance(value, str):
        return import_string(value)
    elif isinstance(value, (list, tuple)):
        return [import_string(item) for item in value]
    return value


class SSOAuthSettings:
    def __init__(self, user_settings, defaults, import_strings):
        self.okta_api_jwks_url = None
        self.user_settings = user_settings
        self.defaults = defaults
        self.import_strings = import_strings
        self._cached_attrs = set()
        self._initialize_oauth_clients()

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Invalid SSO auth setting: '{attr}'")

        try:
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        if attr in self.import_strings:
            val = perform_import(val, attr)

        setattr(self, attr, val)
        self._cached_attrs.add(attr)
        return val

    def _initialize_oauth_clients(self):
        self.okta_api_client = self._register_okta_api_client()
        self.okta_admin_client = self._register_okta_admin_client()

    def _register_okta_api_client(self):
        return self.OAUTH_CLASS().register(
            "okta_api",
            client_id=self.AUTH_API_CLIENT_ID,
            client_kwargs={"scope": "openid profile email"},
            server_metadata_url=f"https://{self.AUTH_DOMAIN}/.well-known/openid-configuration",
        )

    def _register_okta_admin_client(self):
        return self.OAUTH_CLASS().register(
            "okta_admin",
            client_id=self.AUTH_ADMIN_CLIENT_ID,
            client_secret=self.AUTH_API_CLIENT_SECRET,
            client_kwargs={"scope": "openid profile email"},
            server_metadata_url=f"https://{self.AUTH_DOMAIN}/.well-known/openid-configuration",
        )

    def load_okta_api_metadata(self):
        if not self.okta_api_client.server_metadata:
            self.okta_api_client.load_server_metadata()
        self.okta_api_jwks_url = self.okta_api_client.server_metadata.get("jwks_uri")
        if not self.okta_api_jwks_url:
            raise ValueError("JWKS URL not found in server metadata")


# Factory function to create an instance of SSOAuthSettings
sso_auth_settings = SSOAuthSettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
