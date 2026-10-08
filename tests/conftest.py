"""Shared pytest configuration."""

import os


try:
    from hypothesis import HealthCheck, settings

    # Property tests are deterministic by default so a CI failure reproduces locally; set HYPOTHESIS_PROFILE=explore
    # for randomized exploration (failures are still saved in the example database and replayed).
    settings.register_profile("deterministic", derandomize=True, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    settings.register_profile("explore", deadline=None)
    settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "deterministic"))
except ImportError:  # pragma: no cover - exercised only without the dev extras
    if os.environ.get("CI"):
        raise
