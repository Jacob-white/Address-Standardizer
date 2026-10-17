"""Tests for validate_address convenience helper and AddressValidationResult."""

from address_standardizer import (
    AddressValidationResult,
    standardize_address,
    validate_address,
)


def test_validate_address_clean_us():
    res = validate_address("1600 Amphitheatre Pkwy, Mountain View, CA 94043")
    assert isinstance(res, AddressValidationResult)
    assert res.is_valid is True
    assert res.is_deliverable is True
    assert res.deliverability == "DELIVERABLE"
    assert res.rejection_reason is None
    assert res.routing_tier == "AUTO_PASS"
    assert res.confidence_score >= 0.95
    assert res.standardized_address is not None

    d = res.as_dict()
    assert d["is_valid"] is True
    assert d["deliverability"] == "DELIVERABLE"
    assert d["standardized_address"]["city"] == "MOUNTAIN VIEW"


def test_validate_address_dict_input():
    addr = {
        "street1": "100 Main St",
        "city": "Seattle",
        "state": "WA",
        "postal_code": "98101",
    }
    res = validate_address(addr, country="USA")
    assert res.is_valid is True
    assert res.standardized_address.city == "SEATTLE"


def test_validate_address_kwargs_input():
    res = validate_address(
        street1="100 Main St",
        city="Seattle",
        state="WA",
        postal_code="98101",
        country="USA",
    )
    assert res.is_valid is True
    assert res.standardized_address.city == "SEATTLE"


def test_validate_address_missing_street_number():
    res = validate_address("Main St, Boston, MA 02108")
    assert res.is_valid is False
    assert res.rejection_reason is not None
    assert "ERR_MISSING_HOUSE_NUM" in res.failure_reason_codes or "NO_STREET_NUMBER" in res.failure_reason_codes


def test_validate_address_strict_mode():
    res_normal = validate_address("100 Main St, Seattle, WA 98101")
    assert res_normal.is_valid is True

    # Place mismatch with reference validation degrades to FUZZY_REVIEW without fatal errors
    res_fuzzy = validate_address("100 Main St, Buffalo, NY 10001", enable_reference_validation=True)
    assert res_fuzzy.routing_tier == "FUZZY_REVIEW"
    assert res_fuzzy.is_valid is True
    assert res_fuzzy.is_deliverable is True

    res_strict = validate_address("100 Main St, Buffalo, NY 10001", enable_reference_validation=True, strict=True)
    assert res_strict.is_valid is False
    assert res_strict.is_deliverable is False
    assert "strict requirements" in res_strict.rejection_reason


def test_validate_address_dict_with_country_present():
    addr = {
        "street1": "100 Main St",
        "city": "Seattle",
        "state": "WA",
        "postal_code": "98101",
        "country": "USA",
    }
    res = validate_address(addr, country="USA")
    assert res.is_valid is True
    assert res.standardized_address.country == "USA"


def test_validate_address_manual_stewardship_rejection():
    # Commaless single line missing state has WARN_SINGLE_LINE_NO_COMMA but no fatal ERR_*
    res = validate_address("123 Main St Austin", country="USA")
    assert res.is_valid is False
    assert res.routing_tier == "MANUAL_STEWARDSHIP"
    assert res.rejection_reason == "Low confidence score requires manual stewardship"


def test_validate_address_undeliverable_without_fatal_errors():
    # Locality only has WARN_LOCALITY_ONLY and NO_STREET_NUMBER (no fatal ERR_*) but is UNDELIVERABLE
    res = validate_address("Seattle, WA", allow_locality=True)
    assert res.is_valid is False
    assert res.deliverability == "UNDELIVERABLE"
    assert res.rejection_reason == "Address is undeliverable"


def test_address_validation_result_without_standardized_address():
    res = AddressValidationResult(
        is_valid=False,
        deliverability="UNDELIVERABLE",
        rejection_reason="Custom failure",
        standardized_address=None,
    )
    assert res.is_deliverable is False
    d = res.as_dict()
    assert d["is_valid"] is False
    assert d["standardized_address"] is None


def test_validate_address_undeliverable():
    # State / ZIP mismatch
    res = validate_address("100 Main St, Beverly Hills, NY 90210")
    assert res.is_valid is False
    assert res.rejection_reason is not None


def test_validate_address_with_reference_validation():
    res = validate_address("100 Main St, Seattle, WA 98101", enable_reference_validation=True)
    assert res.is_valid is True
    assert res.standardized_address.reference_validation is not None
    assert res.standardized_address.reference_validation.is_confirmed is True


def test_reference_validation_is_confirmed_property():
    std = standardize_address("100 Main St, Seattle, WA 98101", enable_reference_validation=True)
    assert std.reference_validation is not None
    assert std.reference_validation.is_confirmed is True
