"""
Tests for Graceful Cascading Fallback & Verification Topology.
==============================================================
"""

from unittest.mock import MagicMock
from address_standardizer.cascade import (
    CascadePrecision,
    CascadeResult,
    VerificationCascade,
    resolve_verification_cascade,
    ACCURACY_RADII_METERS,
)


class TestVerificationCascade:
    def setup_method(self):
        self.cascade = VerificationCascade()

    def test_cascade_result_as_dict(self):
        res = CascadeResult(
            latitude=39.747182,
            longitude=-75.549927,
            precision=CascadePrecision.CONFIRMED_ROOFTOP,
            accuracy_radius_meters=5.0,
            source="LOCAL_ROOFTOP_REGISTRY",
            stage=1,
            census_tract="000100",
        )
        d = res.as_dict()
        assert d["latitude"] == 39.747182
        assert d["longitude"] == -75.549927
        assert d["precision"] == CascadePrecision.CONFIRMED_ROOFTOP
        assert d["stage"] == 1
        assert d["census_tract"] == "000100"

    def test_stage_1_rooftop_resolution(self):
        # Register rooftop by normalized_address_key
        key = "1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA"
        self.cascade.register_rooftop(key, 39.747182, -75.549927)

        res = self.cascade.resolve(
            street1="1209 N ORANGE ST",
            city="WILMINGTON",
            state="DE",
            postal_code="19801",
            normalized_address_key=key,
        )
        assert res is not None
        assert res.stage == 1
        assert res.precision == CascadePrecision.CONFIRMED_ROOFTOP
        assert res.accuracy_radius_meters == ACCURACY_RADII_METERS[CascadePrecision.CONFIRMED_ROOFTOP]
        assert res.latitude == 39.747182

        # Register rooftop by composite street1|city|state|zip5
        self.cascade.register_rooftop("100 WALL ST|NEW YORK|NY|10005", 40.7061, -74.0060)
        res2 = self.cascade.resolve(
            street1="100 Wall St",
            city="New York",
            state="NY",
            postal_code="10005",
        )
        assert res2 is not None
        assert res2.stage == 1
        assert res2.latitude == 40.7061

    def test_stage_2_census_geocoder_fallback(self):
        mock_geocoder = MagicMock()
        mock_geocoder.geocode_batch.return_value = {
            "1": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "census_tract": "36061000100",
            }
        }

        res = self.cascade.resolve(
            street1="200 Park Ave",
            city="New York",
            state="NY",
            postal_code="10166",
            census_geocoder=mock_geocoder,
        )
        assert res is not None
        assert res.stage == 2
        assert res.precision == CascadePrecision.FALLBACK_TIGER
        assert res.latitude == 40.7128
        assert res.census_tract == "36061000100"

        # Geocoder error handled gracefully
        mock_geocoder.geocode_batch.side_effect = Exception("Census API Timeout")
        res_err = self.cascade.resolve(
            street1="200 Park Ave",
            city="New York",
            state="NY",
            postal_code="10166",
            census_geocoder=mock_geocoder,
        )
        # Should fall through to Stage 3 (Metro ZIP3 101)
        assert res_err is not None
        assert res_err.stage == 3

    def test_stage_3_metro_zip3_centroid(self):
        # 10005 -> ZIP3 100 (Metro ZIP3 NYC)
        res = self.cascade.resolve(postal_code="10005")
        assert res is not None
        assert res.stage == 3
        assert res.precision == CascadePrecision.FALLBACK_ZIP3
        assert res.source == "METRO_ZIP3_CENTROID"

        # 4-digit zip padded with leading zero (e.g. "2138" -> "02138" -> "021" Boston)
        res_pad = self.cascade.resolve(postal_code="2138")
        assert res_pad is not None
        assert res_pad.stage == 3
        assert res_pad.precision == CascadePrecision.FALLBACK_ZIP3

    def test_stage_3b_zip3_state_centroid(self):
        # 03901 -> ZIP3 "039" -> Maine (not in METRO_ZIP3, maps via ZIP3_TO_STATE)
        res = self.cascade.resolve(postal_code="03901")
        assert res is not None
        assert res.stage == 4
        assert res.source == "STATE_CENTROID_FROM_ZIP3"
        assert res.precision == CascadePrecision.FALLBACK_STATE

    def test_stage_4_state_geographic_centroid(self):
        # State abbreviation
        res_tx = self.cascade.resolve(state="TX")
        assert res_tx is not None
        assert res_tx.stage == 4
        assert res_tx.precision == CascadePrecision.FALLBACK_STATE
        assert res_tx.source == "STATE_CENTROID"

        # Full state name
        res_cal = self.cascade.resolve(state="California")
        assert res_cal is not None
        assert res_cal.stage == 4
        assert res_cal.precision == CascadePrecision.FALLBACK_STATE

    def test_stage_5_unresolvable_safe_none(self):
        res_none = self.cascade.resolve(street1="Nowhere", state="UnknownState", postal_code="InvalidZip")
        assert res_none is None

        res_empty = self.cascade.resolve()
        assert res_empty is None

    def test_global_resolve_verification_cascade(self):
        res = resolve_verification_cascade(postal_code="94102")
        assert res is not None
        assert res.stage == 3
        assert res.precision == CascadePrecision.FALLBACK_ZIP3
