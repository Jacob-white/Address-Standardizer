"""Tests for Pydantic v2 schemas and validation models."""

import pytest
from address_standardizer import (
    AddressInputSchema,
    AddressSchema,
    StandardizedAddressPydantic,
    ValidationResultSchema,
    standardize_address,
    validate_address,
)
import address_standardizer.schemas as schemas_module


def test_address_input_schema():
    assert AddressSchema is AddressInputSchema

    schema = AddressInputSchema(
        address="1600 Amphitheatre Pkwy, Mountain View, CA 94043",
        enable_geocoding=True,
    )
    dumped = schema.model_dump()
    assert dumped["address"] == "1600 Amphitheatre Pkwy, Mountain View, CA 94043"
    assert dumped["enable_geocoding"] is True
    assert dumped["country"] == "USA"


def test_standardized_address_pydantic_from_standardized():
    std = standardize_address(
        "100 Main St Apt 4B, Seattle, WA 98101",
        enable_geocoding=True,
    )
    model = StandardizedAddressPydantic.from_standardized(std)
    assert model.street1 == "100 MAIN ST"
    assert model.street2 == "APT 4B"
    assert model.city == "SEATTLE"
    assert model.state == "WA"
    assert model.postal_code == "98101"
    assert model.country == "USA"
    assert model.confidence_score > 0.8
    assert model.latitude is not None or model.latitude is None


def test_validation_result_schema_valid():
    res = validate_address("1600 Amphitheatre Pkwy, Mountain View, CA 94043")
    schema = ValidationResultSchema.from_validation_result(res)
    assert schema.is_valid is True
    assert schema.deliverability == "DELIVERABLE"
    assert schema.rejection_reason is None
    assert schema.standardized_address is not None
    assert schema.standardized_address.city == "MOUNTAIN VIEW"


def test_validation_result_schema_invalid():
    res = validate_address("Main St, Boston, MA 02108")
    schema = ValidationResultSchema.from_validation_result(res)
    assert schema.is_valid is False
    assert schema.rejection_reason is not None
    assert "ERR_MISSING_HOUSE_NUM" in schema.failure_reason_codes or "NO_STREET_NUMBER" in schema.failure_reason_codes


def test_validation_result_schema_without_standardized_address():
    from address_standardizer import AddressValidationResult

    res = AddressValidationResult(
        is_valid=False,
        deliverability="UNDELIVERABLE",
        rejection_reason="No address parsed",
        standardized_address=None,
    )
    schema = ValidationResultSchema.from_validation_result(res)
    assert schema.is_valid is False
    assert schema.standardized_address is None



def test_schemas_import_error():
    import builtins
    orig_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "pydantic":
            raise ImportError("No pydantic")
        return orig_import(name, *args, **kwargs)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(builtins, "__import__", mock_import)
        with pytest.raises(ImportError, match="Pydantic v2 is required"):
            import importlib
            importlib.reload(schemas_module)

    # Reload cleanly afterwards
    import importlib
    importlib.reload(schemas_module)
