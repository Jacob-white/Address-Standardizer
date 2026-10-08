"""
Unit Tests for Dynamic Native Acceleration Dispatcher (_native_dispatch.py).
=============================================================================
Tests dynamic module loading, error-resilient fallback to pure Python core,
runtime engine introspection, testing override hooks, and dispatch functions
with 100% statement test coverage.
"""

import sys
from unittest.mock import MagicMock, patch

from address_standardizer import _native_dispatch, _pure_python_core
from address_standardizer.models import StandardizedAddress


class TestNativeDispatchFallback:
    """Tests default pure Python fallback operation when native extension is absent."""

    def setup_method(self):
        self._patcher = patch.dict(sys.modules, {"_address_standardizer_rs": None})
        self._patcher.start()
        _native_dispatch.reset_engine()

    def teardown_method(self):
        self._patcher.stop()
        _native_dispatch.reset_engine()

    def test_default_pure_python_state(self):
        assert _native_dispatch.is_native_available() is False
        assert _native_dispatch.is_using_native() is False
        assert _native_dispatch.get_active_engine() is _pure_python_core

    def test_get_engine_info_pure_python(self):
        info = _native_dispatch.get_engine_info()
        assert info["engine"] == "PurePythonCore"
        assert info["is_native"] is False
        assert info["native_available"] is False
        assert info["force_pure_python"] is False
        assert info["version"] == "3.3.0"
        assert info["throughput_sla_target"] == ">= 2,000 rec/s"
        assert info["simd_acceleration"] is False
        assert info["zero_copy_slices"] is False

    def test_force_pure_python_toggle(self):
        _native_dispatch.force_pure_python(True)
        assert _native_dispatch._FORCE_PURE_PYTHON is True
        assert _native_dispatch.is_using_native() is False

        _native_dispatch.force_pure_python(False)
        assert _native_dispatch._FORCE_PURE_PYTHON is False

    def test_dispatch_calls_to_pure_python(self):
        # 1. standardize_record_dispatch
        rec = _native_dispatch.standardize_record_dispatch(
            street1="100 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="USA",
        )
        assert isinstance(rec, StandardizedAddress)
        assert rec.street1 == "100 MAIN ST"

        # 2. standardize_batch_dispatch
        batch = _native_dispatch.standardize_batch_dispatch(
            [("100 Main St", "", "New York", "NY", "10001", "USA")]
        )
        assert len(batch) == 1
        assert batch[0].street1 == "100 MAIN ST"

        # 3. compute_soundex_dispatch
        assert _native_dispatch.compute_soundex_dispatch("Montgomery") == "M532"

        # 4. generate_phonetic_key_dispatch
        phon = _native_dispatch.generate_phonetic_key_dispatch(
            street1="555 Montgomery St", postal_or_zip="94111", city="San Francisco"
        )
        assert phon == "555|M532|94111"

        # 5. generate_keys_dispatch
        k1, k2, k3 = _native_dispatch.generate_keys_dispatch(
            street1="100 Wall St",
            street2="Suite 400",
            city="New York",
            state="NY",
            postal_code="10005",
            country="USA",
        )
        assert k1 == "100 WALL ST|STE 400|NEW YORK|NY|10005|USA"
        assert k2 == "100 WALL ST||NEW YORK|NY|10005|USA"
        assert k3 == "100|W400|10005"


class TestNativeDispatchWithMockExtension:
    """Tests native module injection, mock routing, and override mechanisms."""

    def setup_method(self):
        self._patcher = patch.dict(sys.modules, {"_address_standardizer_rs": None})
        self._patcher.start()
        _native_dispatch.reset_engine()

    def teardown_method(self):
        self._patcher.stop()
        _native_dispatch.reset_engine()

    def test_mock_native_module_injection_and_dispatch(self):
        mock_native = MagicMock()
        dummy_std = StandardizedAddress(
            street1="NATIVE ST",
            street2="",
            city="NATIVE CITY",
            state="NY",
            postal_code="10001",
            country="USA",
            normalized_address_key="NATIVE_KEY",
            address_status="standardized",
            raw_street_address="NATIVE ST, NATIVE CITY, NY 10001",
            is_us=True,
        )
        mock_native.standardize_record.return_value = dummy_std
        mock_native.standardize_batch.return_value = [dummy_std]
        mock_native.compute_soundex.return_value = "N999"
        mock_native.generate_phonetic_address_key.return_value = "NATIVE_PHON"
        mock_native.generate_keys.return_value = ("K1", "K2", "K3")

        # Inject mock native module
        _native_dispatch.set_native_module(mock_native)
        assert _native_dispatch.is_native_available() is True
        assert _native_dispatch.is_using_native() is True
        assert _native_dispatch.get_active_engine() is mock_native

        # Verify engine info reflects native acceleration
        info = _native_dispatch.get_engine_info()
        assert info["engine"] == "Rust_PyO3"
        assert info["is_native"] is True
        assert info["native_available"] is True
        assert info["throughput_sla_target"] == ">= 2,000 rec/s"  # no unmeasured speed-up claims
        assert info["simd_acceleration"] is False
        assert info["zero_copy_slices"] is False

        # Test dispatched calls route to native
        assert _native_dispatch.standardize_record_dispatch(street1="Test") == dummy_std
        mock_native.standardize_record.assert_called_once()

        assert _native_dispatch.standardize_batch_dispatch(["Test"]) == [dummy_std]
        mock_native.standardize_batch.assert_called_once()

        assert _native_dispatch.compute_soundex_dispatch("Test") == "N999"
        mock_native.compute_soundex.assert_called_once_with("Test")

        assert _native_dispatch.generate_phonetic_key_dispatch("Test", "10001") == "NATIVE_PHON"
        mock_native.generate_phonetic_address_key.assert_called_once_with("Test", postal_or_zip="10001", city="")

        assert _native_dispatch.generate_keys_dispatch("Test") == ("K1", "K2", "K3")
        mock_native.generate_keys.assert_called_once()

        # Test force_pure_python bypasses native
        _native_dispatch.force_pure_python(True)
        assert _native_dispatch.is_using_native() is False
        assert _native_dispatch.get_active_engine() is _pure_python_core

        _native_dispatch.force_pure_python(False)
        assert _native_dispatch.is_using_native() is True

    def test_override_engine_for_testing(self):
        mock_native = MagicMock()
        _native_dispatch.override_engine_for_testing(mock_native)
        assert _native_dispatch.is_using_native() is True

        # Reset using None
        _native_dispatch.override_engine_for_testing(None)
        assert _native_dispatch.is_using_native() is False

    def test_reset_engine_when_native_module_in_sys_modules(self):
        mock_native = MagicMock()
        with patch.dict(sys.modules, {"_address_standardizer_rs": mock_native}):
            _native_dispatch.reset_engine()
            assert _native_dispatch.is_native_available() is True
            assert _native_dispatch.is_using_native() is True
            assert _native_dispatch.get_active_engine() is mock_native

    def test_module_import_with_native_available(self):
        import importlib

        mock_native = MagicMock()
        with patch.dict(sys.modules, {"_address_standardizer_rs": mock_native}):
            importlib.reload(_native_dispatch)
            assert _native_dispatch.is_native_available() is True
            assert _native_dispatch.is_using_native() is True

        # Restore module state
        with patch.dict(sys.modules, {"_address_standardizer_rs": None}):
            importlib.reload(_native_dispatch)
            assert _native_dispatch.is_native_available() is False
        _native_dispatch.reset_engine()
