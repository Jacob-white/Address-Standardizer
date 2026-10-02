"""
Tests for Data Models (StandardizedAddress).
============================================
"""

from address_standardizer.models import StandardizedAddress


class TestModels:
    def test_standardized_address_defaults(self):
        addr = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall Street, Suite 400, New York, NY 10005",
            is_us=True,
        )
        assert addr.is_private_residence is False
        assert addr.building_key is None
        assert addr.phonetic_key is None
        assert addr.is_registered_agent_hub is False

    def test_standardized_address_as_dict(self):
        addr = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall Street, Suite 400, New York, NY 10005",
            is_us=True,
            is_private_residence=False,
            building_key="100 WALL ST||NEW YORK|NY|10005|USA",
            phonetic_key="100|W400|10005",
            is_registered_agent_hub=False,
        )
        d = addr.as_dict()
        expected = {
            "street1": "100 WALL ST",
            "street2": "STE 400",
            "city": "NEW YORK",
            "state": "NY",
            "postal_code": "10005",
            "country": "USA",
            "normalized_address_key": "100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            "building_key": "100 WALL ST||NEW YORK|NY|10005|USA",
            "phonetic_key": "100|W400|10005",
            "address_status": "standardized",
            "raw_street_address": "100 Wall Street, Suite 400, New York, NY 10005",
            "is_us": True,
            "is_private_residence": False,
            "is_registered_agent_hub": False,
        }
        assert d == expected
        assert len(d) == 14
