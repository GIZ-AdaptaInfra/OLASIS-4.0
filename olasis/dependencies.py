"""Utilities to ensure optional dependencies are available.

This module centralises dependency discovery so that the application can
surface helpful guidance when optional packages are missing.  In
particular, Windows users often execute ``python app.py`` without running
``pip install -r requirements.txt`` beforehand, which would otherwise
result in an opaque ``ModuleNotFoundError``.

By funnelling imports through :func:`require_requests`, we can provide a
clear, actionable message that explains how to install the requirements
without wrapping the import in try/except blocks (which the codebase
avoids for style reasons).
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Callable


def _format_pip_command() -> str:
    """Return a shell-safe command string to install project requirements."""

    repo_root = Path(__file__).resolve().parents[1]
    requirements = repo_root / "requirements.txt"
    quoted_requirements = f'"{requirements}"' if " " in str(requirements) else str(requirements)
    python_executable = sys.executable or "python"
    return f"{python_executable} -m pip install -r {quoted_requirements}"


def _missing_dependency_error(package: str) -> ModuleNotFoundError:
    """Return a ``ModuleNotFoundError`` with installation instructions."""

    install_hint = _format_pip_command()
    return ModuleNotFoundError(
        f"The '{package}' package is required to run OLASIS 4.0. "
        "Install the project dependencies with:\n    " + install_hint
    )


def require_requests() -> ModuleType:
    """Import and return the ``requests`` module.

    Raises a :class:`ModuleNotFoundError` with installation instructions if
    the dependency is unavailable.  This mirrors regular import semantics,
    but the message is significantly clearer for local setups.
    """

    spec = importlib.util.find_spec("requests")
    if spec is None:
        raise _missing_dependency_error("requests")

    return importlib.import_module("requests")


def require_dotenv_loader() -> Callable[..., bool]:
    """Return :func:`dotenv.load_dotenv`, guiding installation if missing."""

    spec = importlib.util.find_spec("dotenv")
    if spec is None:
        raise _missing_dependency_error("python-dotenv")

    module = importlib.import_module("dotenv")
    if not hasattr(module, "load_dotenv"):
        raise ImportError(
            "The 'python-dotenv' package is installed but does not expose "
            "load_dotenv(). Please ensure a compatible version (>= 1.0.0) "
            "is installed."
        )

    return module.load_dotenv


def require_flask() -> ModuleType:
    """Import and return the ``flask`` module with helpful guidance."""

    spec = importlib.util.find_spec("flask")
    if spec is None:
        raise _missing_dependency_error("flask")

    module = importlib.import_module("flask")

    required_attributes = {"Flask", "jsonify", "render_template", "request"}
    missing = sorted(attr for attr in required_attributes if not hasattr(module, attr))
    if missing:
        raise ImportError(
            "The installed 'flask' package is missing required attributes: "
            + ", ".join(missing)
        )

    return module
