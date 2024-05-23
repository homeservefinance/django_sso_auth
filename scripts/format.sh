#!/bin/bash -e

PACKAGE_PATH="django_sso_auth"

ruff check "$PACKAGE_PATH" mock_project tests --fix
black "$PACKAGE_PATH" mock_project tests