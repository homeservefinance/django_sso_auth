# Django SSO Auth

Welcome to the documentation for `django_sso_auth`, a Django package designed to provide seamless Single Sign-On (SSO) authentication using Okta. This package aims to simplify the integration of Okta SSO into your Django applications, ensuring secure and efficient user authentication and session management.

## Overview

`django_sso_auth` is a comprehensive solution for integrating Okta SSO into Django projects. It provides the necessary tools and configurations to authenticate users via Okta, manage user sessions, and ensure secure access to your Django admin and API endpoints.

## Key Features

- **Okta SSO Integration**: Easily integrate Okta SSO for user authentication.
- **Custom Authentication Backends**: Provides custom authentication backends for Django and Django REST Framework.
- **Token Verification**: Securely verify JWT tokens issued by Okta.
- **User Management**: Automatically create and manage user accounts based on Okta claims.
## Installation

To install `django_sso_auth`, run the following command:

<div class="termy">

```console
$ pip install git+https://github.com/homeservefinance/django_sso_auth

---> 100%
```

</div>

## Configuration

Update your `settings.py` with the necessary Okta settings:

```python
SSO_AUTH = {
    'AUTH_API_CLIENT_ID': 'your-okta-api-client-id',
    'AUTH_ADMIN_CLIENT_ID': 'your-okta-admin-client-id',
    'AUTH_API_CLIENT_SECRET': 'your-okta-api-client-secret',
    'AUTH_DOMAIN': 'your-okta-domain',
    'AUTH_ALGORITHMS': ['RS256'],
    'OAUTH_CLASS': 'authlib.integrations.django_client.OAuth',
}

# Add the authentication backends
AUTHENTICATION_BACKENDS = [
    'django_sso_auth.admin.backend.OktaBackend',
    # other backends
]

# Add the DRF authentication class
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'django_sso_auth.drf.authentication.OktaJWTAuthentication',
        # other classes
    ),
}
```

## Quick Start

WIP

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
