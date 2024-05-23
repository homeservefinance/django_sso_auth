from django_sso_auth.conf.settings import SSOAuthSettings

sso_settings = SSOAuthSettings()
sso_settings.register_oauth()
__all__ = ["sso_settings"]
