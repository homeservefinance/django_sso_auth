from django.urls import path

from django_sso_auth.views import okta_auth, okta_callback

urlpatterns = [
    path("sso/", okta_auth, name="okta-auth"),
    path("sso/callback/", okta_callback, name="okta-callback"),
]
