"""
Tests for Offline Rooftop Reference Index & Coordinate Resolver.
================================================================
"""

import sqlite3
import pytest
from address_standardizer import (
    StandardizedAddress,
    VerificationCascade,
    CascadePrecision,
)
from address_standardizer.offline_index import (
    RooftopRecord,
    ParcelValidationResult,
    OfflineReferenceIndex,
    get_default_offline_index,
    resolve_offline_coordinates,
    validate_parcel_offline,
)


class TestOfflineReferenceIndex:
    def test_rooftop_record_as_dict(self):
        rec = RooftopRecord(
            address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            building_key="100 WALL ST||NEW YORK|NY|10005|USA",
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            latitude=40.7061,
            longitude=-74.0060,
            precision="ROOFTOP",
            accuracy_radius_meters=3.0,
            parcel_id="NY-001",
            is_multi_unit=True,
            known_units=["STE 400"],
            rdi="Commercial",
            is_cmra=False,
            is_vacant=False,
            metadata={"source": "TIGER_MAF"},
        )
        d = rec.as_dict()
        assert d["address_key"] == "100 WALL ST|STE 400|NEW YORK|NY|10005|USA"
        assert d["latitude"] == 40.7061
        assert d["parcel_id"] == "NY-001"
        assert d["is_multi_unit"] is True
        assert d["metadata"] == {"source": "TIGER_MAF"}

    def test_parcel_validation_result_as_dict(self):
        res = ParcelValidationResult(
            is_valid_parcel=True,
            parcel_id="DE-001",
            is_multi_unit=True,
            matched_rooftop=True,
            latitude=39.7478,
            longitude=-75.5492,
            accuracy_radius_meters=2.0,
        )
        d = res.as_dict()
        assert d["is_valid_parcel"] is True
        assert d["parcel_id"] == "DE-001"
        assert d["matched_rooftop"] is True

    def test_seed_resolution_and_validation(self):
        index = OfflineReferenceIndex(seed=True)
        assert index.count() >= 5

        # 1. Resolve by normalized_address_key
        addr1 = StandardizedAddress(
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
            building_key="100 WALL ST||NEW YORK|NY|10005|USA",
        )
        rec1 = index.resolve_coordinates(addr1)
        assert rec1 is not None
        assert rec1.latitude == 40.7061
        assert rec1.parcel_id == "NY-MAN-00100"

        # 2. Resolve by building_key
        addr_bld = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 999",  # unindexed suite
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|STE 999|NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St, Ste 999",
            is_us=True,
            building_key="100 WALL ST||NEW YORK|NY|10005|USA",
        )
        rec_bld = index.resolve_coordinates(addr_bld)
        assert rec_bld is not None
        assert rec_bld.street1 == "100 WALL ST"

        # 3. Resolve by string address key directly
        rec_str = index.resolve_coordinates("1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA")
        assert rec_str is not None
        assert rec_str.state == "DE"

        # 4. Resolve by (postal_code, street1)
        addr_zip_st = StandardizedAddress(
            street1="30 N GOULD ST",
            street2="",
            city="SHERIDAN",
            state="WY",
            postal_code="82801-1234",
            country="USA",
            normalized_address_key="30 N GOULD ST||SHERIDAN|WY|82801|USA",
            address_status="standardized",
            raw_street_address="30 N Gould St",
            is_us=True,
            building_key=None,
        )
        rec_zip = index.resolve_coordinates(addr_zip_st)
        assert rec_zip is not None
        assert rec_zip.state == "WY"

        # 5. Unresolvable address
        rec_none = index.resolve_coordinates("9999 NONEXISTENT ST||NOWHERE|XX|00000|USA")
        assert rec_none is None

        # 6. Parcel validation
        val_pass = index.validate_parcel(addr1)
        assert val_pass.is_valid_parcel is True
        assert val_pass.parcel_id == "NY-MAN-00100"
        assert val_pass.matched_rooftop is True

        val_fail = index.validate_parcel("9999 NONEXISTENT ST||NOWHERE|XX|00000|USA")
        assert val_fail.is_valid_parcel is False
        assert val_fail.parcel_id is None

    def test_custom_record_insertion(self):
        index = OfflineReferenceIndex(seed=False)
        assert index.count() == 0

        index.insert_record(
            address_key="500 ELM ST||SPRINGFIELD|IL|62701|USA",
            building_key="500 ELM ST||SPRINGFIELD|IL|62701|USA",
            street1="500 ELM ST",
            city="SPRINGFIELD",
            state="IL",
            postal_code="62701",
            latitude=39.7817,
            longitude=-89.6501,
            precision="ROOFTOP",
            accuracy_radius_meters=3.0,
            parcel_id="IL-SANG-0500",
        )
        assert index.count() == 1

        rec = index.resolve_coordinates("500 ELM ST||SPRINGFIELD|IL|62701|USA")
        assert rec is not None
        assert rec.latitude == 39.7817

        # Batch insertion
        records = [
            {
                "address_key": "101 ALASKA WAY||SEATTLE|WA|98101|USA",
                "building_key": "101 ALASKA WAY||SEATTLE|WA|98101|USA",
                "street1": "101 ALASKA WAY",
                "city": "SEATTLE",
                "state": "WA",
                "postal_code": "98101",
                "latitude": 47.6062,
                "longitude": -122.3321,
            },
            {
                "address_key": "202 PEACHTREE ST||ATLANTA|GA|30303|USA",
                "building_key": "202 PEACHTREE ST||ATLANTA|GA|30303|USA",
                "street1": "202 PEACHTREE ST",
                "city": "ATLANTA",
                "state": "GA",
                "postal_code": "30303",
                "latitude": 33.7550,
                "longitude": -84.3900,
            },
        ]
        index.insert_records(records)
        assert index.count() == 3

    def test_zero_downtime_hot_swap(self, tmp_path):
        db_orig = tmp_path / "rooftop_v1.db"
        index = OfflineReferenceIndex(db_path=str(db_orig), seed=True)
        assert index.count() >= 5

        # 1. Hot swap non-existent file
        with pytest.raises(FileNotFoundError):
            index.hot_swap(str(tmp_path / "non_existent.db"))

        # 2. Hot swap invalid schema file
        bad_db = tmp_path / "bad.db"
        with sqlite3.connect(str(bad_db)) as conn:
            conn.execute("CREATE TABLE wrong_table (id INTEGER PRIMARY KEY)")

        with pytest.raises(ValueError):
            index.hot_swap(str(bad_db))

        # 3. Valid hot swap
        db_v2 = tmp_path / "rooftop_v2.db"
        index_v2 = OfflineReferenceIndex(db_path=str(db_v2), seed=False)
        index_v2.insert_record(
            address_key="999 BROADWAY||NASHVILLE|TN|37203|USA",
            building_key="999 BROADWAY||NASHVILLE|TN|37203|USA",
            street1="999 BROADWAY",
            city="NASHVILLE",
            state="TN",
            postal_code="37203",
            latitude=36.1627,
            longitude=-86.7816,
            precision="ROOFTOP",
            parcel_id="TN-DAV-999",
        )
        index_v2.close()

        # Execute hot swap
        index.hot_swap(str(db_v2))
        assert index.count() == 1
        rec_swapped = index.resolve_coordinates("999 BROADWAY||NASHVILLE|TN|37203|USA")
        assert rec_swapped is not None
        assert rec_swapped.city == "NASHVILLE"

        index.close()

    def test_default_offline_index_singletons(self):
        idx = get_default_offline_index()
        assert idx is not None
        res_coord = resolve_offline_coordinates("100 WALL ST|STE 400|NEW YORK|NY|10005|USA")
        assert res_coord is not None
        assert res_coord.latitude == 40.7061

        res_par = validate_parcel_offline("100 WALL ST|STE 400|NEW YORK|NY|10005|USA")
        assert res_par.is_valid_parcel is True

    def test_verification_cascade_integration_with_offline_index(self):
        index = OfflineReferenceIndex(seed=True)
        cascade = VerificationCascade(offline_index=index)

        # 100 Wall St is indexed in offline_index
        res = cascade.resolve(
            street1="100 Wall St",
            street2="Ste 400",
            city="New York",
            state="NY",
            postal_code="10005",
            normalized_address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
        )
        assert res is not None
        assert res.stage == 1
        assert res.precision == CascadePrecision.CONFIRMED_ROOFTOP
        assert res.source == "OFFLINE_ROOFTOP_INDEX"
        assert res.latitude == 40.7061
        assert res.census_tract == "NY-MAN-00100"

    def test_corrupted_json_in_row_to_record(self):
        index = OfflineReferenceIndex(seed=False)
        with index._lock:
            index._conn.execute(
                """
                INSERT INTO rooftop_reference (
                    address_key, building_key, street1, street2, city, state, postal_code, country,
                    latitude, longitude, precision, known_units, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "CORRUPT|KEY", "CORRUPT||KEY", "123 CORRUPT ST", "", "TEST", "TX", "77001", "USA",
                    30.0, -95.0, "ROOFTOP", "INVALID_JSON_UNITS{", "INVALID_JSON_META{"
                )
            )
            index._conn.commit()
        rec = index.resolve_coordinates("CORRUPT|KEY")
        assert rec is not None
        assert rec.known_units == []
        assert rec.metadata == {}

    def test_resolve_from_plain_address_string(self):
        index = OfflineReferenceIndex(seed=True)
        rec = index.resolve_coordinates("100 Wall St, New York, NY 10005")
        assert rec is not None
        assert rec.street1 == "100 WALL ST"
        assert rec.latitude == 40.7061

    def test_resolve_and_validate_by_parcel_id_directly(self):
        index = OfflineReferenceIndex(seed=True)
        # Direct parcel ID lookup
        rec = index.resolve_coordinates("DE-NCC-26027")
        assert rec is not None
        assert rec.state == "DE"

        val_res = index.validate_parcel("DE-NCC-26027")
        assert val_res.is_valid_parcel is True
        assert val_res.parcel_id == "DE-NCC-26027"

    def test_resolve_coordinates_with_street_number_transposition_healing(self):
        index = OfflineReferenceIndex(seed=True)
        # 1290 N Orange St transposed from 1209 N Orange St in Wilmington DE 19801
        addr_transposed = StandardizedAddress(
            street1="1290 N ORANGE ST",
            street2="",
            city="WILMINGTON",
            state="DE",
            postal_code="19801",
            country="USA",
            normalized_address_key="1290 N ORANGE ST||WILMINGTON|DE|19801|USA",
            address_status="standardized",
            raw_street_address="1290 N Orange St",
            is_us=True,
            building_key="1290 N ORANGE ST||WILMINGTON|DE|19801|USA",
        )
        rec = index.resolve_coordinates(addr_transposed)
        assert rec is not None
        assert rec.street1 == "1209 N ORANGE ST"
        assert rec.parcel_id == "DE-NCC-26027"

    def test_persistent_db_wal_mode(self, tmp_path):
        db_file = tmp_path / "wal_test.db"
        index = OfflineReferenceIndex(db_path=str(db_file), seed=False)
        with index._lock:
            cur = index._conn.execute("PRAGMA journal_mode")
            mode = cur.fetchone()[0]
            assert mode.lower() == "wal"
        index.close()



class TestResolveCoordinatesMemoStaysFresh:
    """The structured-address memo must never serve stale results, whichever way the DB changes."""

    @staticmethod
    def _addr():
        from address_standardizer import standardize_address

        return standardize_address("7 Cache Test Rd, Austin, TX 78701", use_cache=False)

    def _index(self, tmp_path):
        from address_standardizer.offline_index import OfflineReferenceIndex

        return OfflineReferenceIndex(db_path=str(tmp_path / "idx.db"), seed=False)

    def test_insert_after_cached_miss_is_seen(self, tmp_path):
        idx = self._index(tmp_path)
        addr = self._addr()
        assert idx.resolve_coordinates(addr) is None  # cached miss
        idx.insert_record(
            address_key=addr.normalized_address_key, building_key=addr.building_key, street1=addr.street1,
            city=addr.city, state=addr.state, postal_code=addr.postal_code, latitude=30.0, longitude=-97.0,
        )
        assert idx.resolve_coordinates(addr) is not None

    def test_direct_sql_write_is_seen(self, tmp_path):
        idx = self._index(tmp_path)
        addr = self._addr()
        assert idx.resolve_coordinates(addr) is None
        idx.insert_record(
            address_key="X", building_key="X", street1=addr.street1, city=addr.city, state=addr.state,
            postal_code=addr.postal_code, latitude=1.0, longitude=2.0,
        )
        with idx._conn:
            idx._conn.execute("UPDATE rooftop_reference SET latitude = 9.5 WHERE address_key = 'X'")
        assert idx.resolve_coordinates(addr).latitude == 9.5

    def test_write_from_another_connection_is_seen(self, tmp_path):
        import sqlite3

        idx = self._index(tmp_path)
        addr = self._addr()
        assert idx.resolve_coordinates(addr) is None
        idx.insert_record(
            address_key="Y", building_key="Y", street1=addr.street1, city=addr.city, state=addr.state,
            postal_code=addr.postal_code, latitude=1.0, longitude=2.0,
        )
        assert idx.resolve_coordinates(addr).latitude == 1.0
        other = sqlite3.connect(str(tmp_path / "idx.db"))
        with other:
            other.execute("UPDATE rooftop_reference SET latitude = 7.25 WHERE address_key = 'Y'")
        other.close()
        assert idx.resolve_coordinates(addr).latitude == 7.25

    def test_returned_records_are_isolated_from_the_cache(self, tmp_path):
        idx = self._index(tmp_path)
        addr = self._addr()
        idx.insert_record(
            address_key="Z", building_key="Z", street1=addr.street1, city=addr.city, state=addr.state,
            postal_code=addr.postal_code, latitude=1.0, longitude=2.0, known_units=["A"],
        )
        first = idx.resolve_coordinates(addr)
        first.known_units.append("MUTATED")
        first.latitude = 99.0
        second = idx.resolve_coordinates(addr)
        assert second.known_units == ["A"]
        assert second.latitude == 1.0
