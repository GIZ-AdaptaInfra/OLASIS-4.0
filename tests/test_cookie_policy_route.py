"""Regression tests for the cookie policy route availability."""

from __future__ import annotations

import importlib
import sys

import pytest


MODULES = ["app", "app_simple", "app_test"]


@pytest.mark.parametrize("module_name", MODULES)
def test_cookie_policy_route_available(module_name):
    """Ensure each Flask entry point exposes the cookie policy page."""

    # Reload modules between assertions so decorators register correctly.
    if module_name in sys.modules:
        del sys.modules[module_name]

    module = importlib.import_module(module_name)
    app = module.app

    with app.test_client() as client:
        response = client.get("/privacy/cookies")

    assert response.status_code == 200
    assert b"Pol\xc3\xadtica de Cookies" in response.data


@pytest.mark.parametrize("module_name", MODULES)
def test_cookie_policy_legacy_alias(module_name):
    """Legacy `/cookie-policy` path should continue to render the page."""

    if module_name in sys.modules:
        del sys.modules[module_name]

    module = importlib.import_module(module_name)
    app = module.app

    with app.test_client() as client:
        response = client.get("/cookie-policy")

    assert response.status_code == 200
    assert b"Pol\xc3\xadtica de Cookies" in response.data


@pytest.mark.parametrize("module_name", MODULES)
def test_cookie_policy_url_context(module_name):
    """Ensure the helper returns a usable URL even if decorators misfire."""

    if module_name in sys.modules:
        del sys.modules[module_name]

    module = importlib.import_module(module_name)
    app = module.app

    original = app.view_functions.pop("cookie_policy", None)

    try:
        url_value = module._cookie_policy_url()  # type: ignore[attr-defined]
    finally:
        if original is not None:
            app.view_functions["cookie_policy"] = original