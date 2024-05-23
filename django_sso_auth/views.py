from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.urls import reverse
from django_sso_auth.conf import sso_settings


def okta_auth(request):
    redirect_uri = request.build_absolute_uri("/auth/callback/")
    print(f"Redirect URI: {redirect_uri}")
    return sso_settings.OAUTH.okta_admin.authorize_redirect(request, redirect_uri)


def okta_callback(request):
    try:
        # This line captures the token and possibly additional user info from Okta
        token = sso_settings.OAUTH.okta_admin.authorize_access_token(request)
        # This line attempts to authenticate the user based on the token obtained from Okta
        user = authenticate(request, token=token)
        print(f"User: {user}")
        if user is not None:
            # This logs in the user into Django's session framework
            login(request, user)

            # Redirect to the Django admin dashboard or another appropriate page
            return redirect(reverse("admin:index"))
        else:
            # If authentication failed, redirect to the login page with an error message
            messages.error(request, "Authentication failed. Please try again.")
            return redirect("admin:login")
    except Exception as e:
        # Log the error or send it to your error tracking system
        messages.error(request, f"Error during authentication: {str(e)}")
        return redirect("admin:login")
