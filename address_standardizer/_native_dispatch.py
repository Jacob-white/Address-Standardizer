"""
Dynamic Native Acceleration Dispatcher & Fallback Loader.
=========================================================
Dynamic loader that attempts to import the native compiled module (_address_standardizer_rs),
falling back cleanly, transparently, and deterministically to _pure_python_core.
Provides runtime capability introspection, testing override hooks, and batch dispatch delegation.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from address_standardizer import _pure_python_core
from address_standardizer.models import StandardizedAddress

logger = logging.getLogger(__name__)

# Runtime module state
_NATIVE_MODULE: Optional[Any] = None
_NATIVE_AVAILABLE: bool = False
_FORCE_PURE_PYTHON: bool = False

try:
    import _address_standardizer_rs as _native_ext

    _NATIVE_MODULE = _native_ext
    _NATIVE_AVAILABLE = True
    logger.debug("Native compiled acceleration loaded (_address_standardizer_rs).")
except (ImportError, ModuleNotFoundError):
    _NATIVE_MODULE = None
    _NATIVE_AVAILABLE = False
    logger.info("Native compiled core unavailable; operating via pure Python fallback.")


def is_native_available() -> bool:
    """Returns True if native compiled binary module is available in Python runtime."""
    return _NATIVE_AVAILABLE


def is_using_native() -> bool:
    """Returns True if native compiled core is active for dispatch calls."""
    return _NATIVE_AVAILABLE and not _FORCE_PURE_PYTHON and _NATIVE_MODULE is not None


def get_active_engine() -> Any:
    """Returns active acceleration engine module (native or pure python fallback)."""
    if is_using_native():
        return _NATIVE_MODULE
    return _pure_python_core


def get_engine_info() -> Dict[str, Any]:
    """Returns dictionary detailing engine metadata, active status, and SLA capabilities."""
    using_native = is_using_native()
    return {
        "engine": "Rust_PyO3" if using_native else "PurePythonCore",
        "is_native": using_native,
        "native_available": _NATIVE_AVAILABLE,
        "force_pure_python": _FORCE_PURE_PYTHON,
        "version": "3.3.0",
        "throughput_sla_target": ">= 50,000 rec/s" if using_native else ">= 2,000 rec/s",
        "simd_acceleration": using_native,
        "zero_copy_slices": using_native,
    }


def force_pure_python(enabled: bool = True) -> None:
    """Override hook forcing fallback to pure Python engine."""
    global _FORCE_PURE_PYTHON
    _FORCE_PURE_PYTHON = enabled
    logger.debug("Dispatched pure python forced: %s", enabled)


def set_native_module(module: Optional[Any]) -> None:
    """Testing hook to register mock or alternative native module."""
    global _NATIVE_MODULE, _NATIVE_AVAILABLE
    _NATIVE_MODULE = module
    _NATIVE_AVAILABLE = module is not None


def override_engine_for_testing(mock_engine: Optional[Any]) -> None:
    """Convenience testing hook to override or reset the active engine."""
    if mock_engine is not None:
        set_native_module(mock_engine)
    else:
        reset_engine()


def reset_engine() -> None:
    """Reset engine state to system autodetected defaults."""
    global _FORCE_PURE_PYTHON, _NATIVE_MODULE, _NATIVE_AVAILABLE
    _FORCE_PURE_PYTHON = False
    try:
        import _address_standardizer_rs as _native_ext

        _NATIVE_MODULE = _native_ext
        _NATIVE_AVAILABLE = True
    except (ImportError, ModuleNotFoundError):
        _NATIVE_MODULE = None
        _NATIVE_AVAILABLE = False


def standardize_record_dispatch(
    street1: Optional[str] = None,
    street2: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None,
    **kwargs: Any,
) -> StandardizedAddress:
    """Dispatches single record standardization to active engine."""
    engine = get_active_engine()
    return engine.standardize_record(
        street1=street1,
        street2=street2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        **kwargs,
    )


def standardize_batch_dispatch(
    records: List[Any],
    chunk_size: int = 5000,
    **kwargs: Any,
) -> List[StandardizedAddress]:
    """Dispatches batch standardization to active engine with pre-allocated buffers."""
    engine = get_active_engine()
    return engine.standardize_batch(records, chunk_size=chunk_size, **kwargs)


def compute_soundex_dispatch(token: str) -> str:
    """Dispatches Soundex computation to active engine."""
    engine = get_active_engine()
    return engine.compute_soundex(token)


def generate_phonetic_key_dispatch(
    street1: Optional[str],
    postal_or_zip: str = "",
    city: str = "",
) -> Optional[str]:
    """Dispatches phonetic blocking key generation to active engine."""
    engine = get_active_engine()
    return engine.generate_phonetic_address_key(street1, postal_or_zip=postal_or_zip, city=city)


def generate_keys_dispatch(
    street1: Optional[str] = None,
    street2: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Dispatches deterministic entity key generation to active engine."""
    engine = get_active_engine()
    return engine.generate_keys(
        street1=street1,
        street2=street2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
    )
