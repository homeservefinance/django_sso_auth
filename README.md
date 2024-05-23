# Django SSO Authentication - WIP

This is a Django application that provides Okta Single Sign-On (SSO) authentication for HomeServe Django projects.

## Installation

Since this is a private repository, you need to add the following to your `requirements.txt` file:

```txt
-e git+
    git://github.com/homeserve/django-sso-authentication.git@master#egg=django-sso-authentication
```

Then run:

```bash
pip install -r requirements.txt
```

## Configuration

Add the following to your Django `settings.py`:

```python
# This is required for the Django admin site
AUTHENTICATION_BACKENDS = [
    "django_sso_auth.admin.OktaBackend",
]



# These settings are required for the Okta SSO authentication to work
AUTH_API_CLIENT_ID = "your_okta_client_id"
AUTH_ADMIN_CLIENT_ID = "your_okta_admin_client_id"
AUTH_API_CLIENT_SECRET = "your_okta_client_secret"
AUTH_DOMAIN = "your_okta_domain"

# This is required for the Django REST framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "django_sso_auth.drf.TokenAuthentication",
    ],
}
```

Add the following to your Django `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('sso/', include('django_sso_auth.urls')),
]
```
