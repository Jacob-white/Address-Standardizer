"""Optional-dependency helper: skip locally, but fail loudly in CI so a missing extra can't hide untested code."""

import importlib
import os

import pytest


def require(module: str, reason: str = ""):
    """``pytest.importorskip`` on developer machines; a hard import error when ``CI`` is set."""
    if os.environ.get("CI"):
        return importlib.import_module(module)
    return pytest.importorskip(module, reason=reason or f"{module} is not installed")
