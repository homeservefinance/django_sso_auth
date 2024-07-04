from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.urls import reverse
from django_sso_auth.conf import sso_auth_settings
import logging

logger = logging.getLogger(__name__)


def okta_auth(request):
    redirect_uri = request.build_absolute_uri("/sso/callback/")
    return sso_auth_settings.okta_admin_client.authorize_redirect(request, redirect_uri)


def okta_callback(request):
    try:
        sso_auth_settings.load_okta_api_metadata()
        token = sso_auth_settings.okta_admin_client.authorize_access_token(request)

        user = authenticate(request, token=token)
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect(reverse("admin:index"))
            else:
                messages.error(
                    request, "You are not authorized to access the admin panel."
                )
                return redirect("admin:login")
        else:
            messages.error(request, "Authentication failed. Please try again.")
            return redirect("admin:login")
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        messages.error(request, f"Error during authentication: {str(e)}")
        return redirect("admin:login")
