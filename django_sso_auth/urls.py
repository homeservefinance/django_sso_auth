from django.urls import path
from django_sso_auth.views import okta_auth, okta_callback

urlpatterns = [
    path("auth/", okta_auth, name="okta-auth"),
    path("auth/callback/", okta_callback, name="okta-callback"),
]
