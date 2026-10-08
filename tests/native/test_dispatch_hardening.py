"""Native dispatch must never let an extension failure (including a PyO3 panic) escape to callers."""

import pytest

from address_standardizer import _native_dispatch as nd
from address_standardizer import standardize_address
from address_standardizer import _pure_python_core as core
from address_standardizer.phonetics import compute_soundex, generate_phonetic_address_key


class FakePanic(BaseException):
    """Stand-in for pyo3_runtime.PanicException, which derives from BaseException, not Exception."""


class PanickingEngine:
    def __getattr__(self, name):
        def boom(*args, **kwargs):
            raise FakePanic(f"{name} panicked")

        return boom


@pytest.fixture
def panicking_native():
    nd.set_native_module(PanickingEngine())
    yield
    nd.reset_engine()


def test_panics_fall_back_to_pure_python(panicking_native):
    assert nd.is_using_native()
    assert nd.compute_soundex_dispatch("Robert") == "R163"
    assert compute_soundex("Robert") == "R163"
    assert generate_phonetic_address_key("123 Main St", postal_or_zip="12345") == "123|M500|12345"
    assert nd.canonicalize_suffix_dispatch("avenue") == "AVE"
    assert nd.fast_tokenize_dispatch("12 main st") == ["12", "MAIN", "ST"]
    rec = nd.standardize_record_dispatch(street1="100 Main St", city="Austin", state="TX", postal_code="78701")
    assert rec.street1 == "100 MAIN ST"
    batch = nd.standardize_batch_dispatch([("100 Main St", None, "Austin", "TX", "78701", "USA")])
    assert batch[0].street1 == "100 MAIN ST"


def test_keyboard_interrupt_is_not_swallowed():
    class Interrupting:
        def compute_soundex(self, token):
            raise KeyboardInterrupt

    nd.set_native_module(Interrupting())
    try:
        with pytest.raises(KeyboardInterrupt):
            nd.compute_soundex_dispatch("x")
    finally:
        nd.reset_engine()


def test_env_kill_switch_forces_pure_python(monkeypatch):
    monkeypatch.setenv("ADDRESS_STANDARDIZER_FORCE_PURE", "1")
    nd.reset_engine()
    try:
        assert nd.is_using_native() is False
        assert nd.get_active_engine() is core
    finally:
        monkeypatch.delenv("ADDRESS_STANDARDIZER_FORCE_PURE")
        nd.reset_engine()


@pytest.mark.parametrize(
    "record",
    [
        ("N/A", "Fl 3", "São Paulo", "New York", None, "Deutschland"),  # garbage token with other fields
        ("1" * 200, None, "Austin", "TX", "78701", "USA"),  # over-long street
        ("PO Box 123", None, "ZÜRICH", None, "1000", "GB"),  # non-US PO box
        ("", "#5", "Austin", "TX", "78701", "USA"),
        ("100 Main St", None, None, None, None, None),
    ],
)
def test_pure_core_matches_standardize_address(record):
    """The pure core used to be a parallel copy of the pipeline and diverged on these records."""
    s1, s2, city, state, postal, country = record
    ref = standardize_address(s1, s2, city, state, postal, country, use_cache=False)
    got = core.standardize_record(s1, s2, city, state, postal, country, finalize=True)
    assert (got.street1, got.street2, got.address_status, got.normalized_address_key, got.phonetic_key) == (
        ref.street1, ref.street2, ref.address_status, ref.normalized_address_key, ref.phonetic_key,
    )
