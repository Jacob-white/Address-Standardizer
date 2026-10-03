"""
Tests for 4-Stage Geocoding Cascade Resolver.
==============================================
Validates deterministic progression through:
  Stage 1: Confirmed Rooftop / Building / Parcel Match
  Stage 2: Street Centerline Linear Range Interpolation with Parity Offset
  Stage 3: Postal Centroid Match (ZIP5, ZIP3, in-memory METRO_ZIP3)
  Stage 4: Municipal / State Centroid Match (City, State DB & in-memory)
  Fallback: UNRESOLVED
"""

from address_standardizer.models import StandardizedAddress, SpatialResolutionResult
from address_standardizer.spatial.engine import SpatialEngine


class TestCascadeResolver:
    @classmethod
    def setup_class(cls):
        cls.engine = SpatialEngine(seed=True)

    @classmethod
    def teardown_class(cls):
        cls.engine.close()

    def test_stage_1_exact_address_key(self):
        # 100 Wall St Suite 400
        res = self.engine.resolve("100 WALL ST|STE 400|NEW YORK|NY|10005|USA")
        assert isinstance(res, SpatialResolutionResult)
        assert res.stage == 1
        assert res.precision == "CONFIRMED_ROOFTOP"
        assert res.source == "OPENADDRESSES"
        assert res.latitude == 40.7061
        assert res.longitude == -74.0060
        assert res.accuracy_radius_meters <= 5.0
        assert res.parcel_id == "NY-MAN-00100"
        assert len(res.h3_res10) == 15
        assert res.execution_time_ms >= 0.0

    def test_stage_1_building_key_match(self):
        # Same building 100 Wall St, but different unknown suite 999
        query = {
            "normalized_address_key": "100 WALL ST|STE 999|NEW YORK|NY|10005|USA",
            "building_key": "100 WALL ST||NEW YORK|NY|10005|USA",
        }
        res = self.engine.resolve(query)
        assert res.stage == 1
        assert res.precision == "CONFIRMED_ROOFTOP"
        assert res.latitude == 40.7061

    def test_stage_1_parcel_id_match(self):
        # Match directly on parcel ID DE-NCC-26027
        query = {
            "parcel_id": "DE-NCC-26027",
            "street1": "UNKNOWN STREET",
        }
        res = self.engine.resolve(query)
        assert res.stage == 1
        assert res.precision == "CONFIRMED_ROOFTOP"
        assert res.parcel_id == "DE-NCC-26027"
        assert res.latitude == 39.7478

    def test_stage_2_street_interpolation_both_parity(self):
        # Market St has segment 1000 to 1100, parity BOTH
        query = {
            "street1": "1050 MARKET ST",
            "city": "SAN FRANCISCO",
            "state": "CA",
            "postal_code": "94103",
        }
        res = self.engine.resolve(query)
        assert res.stage == 2
        assert res.precision == "RANGE_INTERPOLATED"
        assert res.source == "TIGER_INTERPOLATION"
        assert res.accuracy_radius_meters == 35.0
        assert 37.77 < res.latitude < 37.78
        assert -122.42 < res.longitude < -122.41
        assert len(res.h3_res10) == 15

    def test_stage_2_street_interpolation_even_parity(self):
        # Broadway has segment 200 to 300, parity EVEN
        # Even number: 250
        query_even = {
            "street1": "250 BROADWAY",
            "city": "NEW YORK",
            "state": "NY",
            "postal_code": "10007",
        }
        res_even = self.engine.resolve(query_even)
        assert res_even.stage == 2
        assert res_even.precision == "RANGE_INTERPOLATED"

        # Odd number: 251 -> fails even parity, should cascade to Stage 3 or Stage 4
        query_odd = {
            "street1": "251 BROADWAY",
            "city": "NEW YORK",
            "state": "NY",
            "postal_code": "10007",
        }
        res_odd = self.engine.resolve(query_odd)
        # Should not be stage 2
        assert res_odd.stage in (3, 4)

    def test_stage_2_descending_street_segment_and_odd_parity(self):
        # Insert a descending street segment: from 500 down to 400 with parity ODD
        self.engine.insert_street_segment(
            street_name="DESCENDING WAY",
            from_number=500,
            to_number=400,
            start_lat=30.0,
            start_lon=-90.0,
            end_lat=30.01,
            end_lon=-90.01,
            parity="ODD",
            postal_code="70112",
            city="NEW ORLEANS",
            state="LA",
            source="TIGER",
        )

        # Query matching odd number 451
        query_odd = {
            "street1": "451 DESCENDING WAY",
            "postal_code": "70112",
        }
        res_odd = self.engine.resolve(query_odd)
        assert res_odd.stage == 2
        assert res_odd.precision == "RANGE_INTERPOLATED"

        # Query even number 450 -> skipped
        query_even = {
            "street1": "450 DESCENDING WAY",
            "postal_code": "70112",
        }
        res_even = self.engine.resolve(query_even)
        assert res_even.stage != 2

    def test_stage_3_postal_centroid(self):
        # Insert specific postal centroid
        self.engine.insert_postal_centroid(
            postal_code="99501",
            latitude=61.2181,
            longitude=-149.9003,
            accuracy_radius_m=6000.0,
            city="ANCHORAGE",
            state="AK",
        )
        query = {
            "street1": "999 UNKNOWN RD",
            "postal_code": "99501",
        }
        res = self.engine.resolve(query)
        assert res.stage == 3
        assert res.precision == "POSTAL_CENTROID"
        assert res.latitude == 61.2181
        assert res.accuracy_radius_meters == 6000.0

    def test_stage_3_zip3_prefix_and_in_memory_fallback(self):
        # Seeded ZIP3 '100' exists in postal_centroids from METRO_ZIP3_CENTROIDS
        query_zip3 = {
            "street1": "999 NONEXISTENT AVE",
            "postal_code": "10099",
        }
        res = self.engine.resolve(query_zip3)
        assert res.stage == 3
        assert res.precision == "POSTAL_CENTROID"

        # Fallback to in-memory METRO_ZIP3_CENTROIDS when postal_centroids has no row
        # Delete row '606' from postal_centroids and query 60601
        with self.engine._lock, self.engine._conn:
            self.engine._conn.execute("DELETE FROM postal_centroids WHERE postal_code = '606'")

        query_chicago = {
            "street1": "999 UNMAPPED ST",
            "postal_code": "60601",
        }
        res_chi = self.engine.resolve(query_chicago)
        assert res_chi.stage == 3
        assert res_chi.precision == "POSTAL_CENTROID"
        assert res_chi.source == "METRO_ZIP3_CENTROID"

    def test_stage_4_municipal_and_state_centroids(self):
        # Insert a city/state centroid
        self.engine.insert_municipal_centroid(
            name="BOULDER",
            state="CO",
            latitude=40.0150,
            longitude=-105.2705,
            accuracy_radius_m=15000.0,
        )
        query_city = {
            "street1": "999 UNMAPPED TRAIL",
            "city": "BOULDER",
            "state": "CO",
        }
        res_city = self.engine.resolve(query_city)
        assert res_city.stage == 4
        assert res_city.precision == "MUNICIPAL_CENTROID"
        assert res_city.source == "MUNICIPAL_CENTROID"
        assert res_city.latitude == 40.0150

        # Query state only
        query_state = {
            "street1": "999 RURAL ROAD",
            "state": "WY",
        }
        res_state = self.engine.resolve(query_state)
        assert res_state.stage == 4
        assert res_state.precision == "MUNICIPAL_CENTROID"
        assert res_state.source == "STATE_CENTROID"

        # Fallback to in-memory STATE_CENTROIDS when municipal_centroids has no row
        with self.engine._lock, self.engine._conn:
            self.engine._conn.execute("DELETE FROM municipal_centroids WHERE name = 'HI'")
        query_hi = {
            "street1": "999 HIGHWAY",
            "state": "HAWAII",
        }
        res_hi = self.engine.resolve(query_hi)
        assert res_hi.stage == 4
        assert res_hi.source == "STATE_CENTROID"

    def test_fallback_unresolved(self):
        # Completely unknown location
        query_none = {
            "street1": "",
            "city": "UNKNOWNVILLE",
            "state": "ZZ",
            "postal_code": "",
        }
        res = self.engine.resolve(query_none)
        assert res.stage == 0
        assert res.precision == "UNRESOLVED"
        assert res.latitude == 0.0
        assert res.longitude == 0.0
        assert res.accuracy_radius_meters == 0.0
        assert res.source == "NONE"
        assert res.h3_res10 == ""

    def test_resolve_input_types(self):
        # 1. StandardizedAddress instance
        std = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St, Ste 400",
            is_us=True,
        )
        res_std = self.engine.resolve(std)
        assert res_std.stage == 1

        # 2. Plain string (not key)
        res_str = self.engine.resolve("100 Wall St, New York, NY 10005")
        assert res_str.stage in (1, 2, 3, 4)

        # 3. as_dict serialization
        d = res_std.as_dict()
        assert d["latitude"] == 40.7061
        assert d["stage"] == 1
        assert d["precision"] == "CONFIRMED_ROOFTOP"
        assert "metadata" in d
