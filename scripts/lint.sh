#!/bin/bash -e

PACKAGE_PATH="django_sso_auth"

ruff check "$PACKAGE_PATH" tests mock_project
black "$PACKAGE_PATH" tests mock_project --check