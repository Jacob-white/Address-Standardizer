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

    def test_standardized_address_enterprise_metadata_and_properties(self):
        addr = StandardizedAddress(
            street1="1209 N ORANGE ST",
            street2="STE 400",
            city="WILMINGTON",
            state="DE",
            postal_code="19801",
            country="USA",
            normalized_address_key="1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA",
            address_status="standardized",
            raw_street_address="1209 N Orange St",
            is_us=True,
        )
        assert addr.confidence_score is None
        assert addr.routing_tier is None
        assert addr.failure_reason_codes == []
        assert addr.audit_record is None
        assert addr.cascade_result is None

        # Set properties
        addr.confidence_score = 0.9920
        addr.routing_tier = "AUTO_PASS"
        addr.failure_reason_codes = ["WARN_CRA_HUB_DETECTED"]

        class DummyAudit:
            audit_id = "test-audit-uuid"

        class DummyCascade:
            def as_dict(self):
                return {"latitude": 39.74, "longitude": -75.55, "precision": "CONFIRMED_ROOFTOP"}

        addr.audit_record = DummyAudit()
        addr.cascade_result = DummyCascade()

        assert addr.confidence_score == 0.9920
        assert addr.routing_tier == "AUTO_PASS"
        assert addr.failure_reason_codes == ["WARN_CRA_HUB_DETECTED"]
        assert addr.audit_record.audit_id == "test-audit-uuid"
        assert addr.cascade_result.as_dict()["precision"] == "CONFIRMED_ROOFTOP"

        # as_dict() default remains 14 fields
        assert len(addr.as_dict()) == 14

        # as_dict(include_metadata=True) and as_extended_dict() include all metadata
        ext = addr.as_extended_dict()
        assert ext["confidence_score"] == 0.9920
        assert ext["routing_tier"] == "AUTO_PASS"
        assert ext["failure_reason_codes"] == ["WARN_CRA_HUB_DETECTED"]
        assert ext["audit_id"] == "test-audit-uuid"
        assert ext["cascade"]["precision"] == "CONFIRMED_ROOFTOP"

        # Test non-dict cascade result branch
        addr.cascade_result = "NonDictCascade"
        ext2 = addr.as_dict(include_metadata=True)
        assert ext2["cascade"] == "NonDictCascade"
