from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.urls import reverse
from django_sso_auth.conf import sso_settings


def okta_auth(request):
    redirect_uri = request.build_absolute_uri("/sso/callback/")
    print(f"Redirect URI: {redirect_uri}")
    return sso_settings.OAUTH.okta_admin.authorize_redirect(request, redirect_uri)


def okta_callback(request):
    try:
        token = sso_settings.OAUTH.okta_admin.authorize_access_token(request)
        user = authenticate(request, token=token)
        print(f"User: {user}")
        if user is not None:
            login(request, user)
            return redirect(reverse("admin:index"))
        else:
            messages.error(request, "Authentication failed. Please try again.")
            return redirect("admin:login")
    except Exception as e:
        messages.error(request, f"Error during authentication: {str(e)}")
        return redirect("admin:login")
