"""Coverage-driven tests for audit, cache, registry, fast_path, autocomplete and the spatial subsystem."""

import json
import os
from types import SimpleNamespace

import pytest

from address_standardizer import registry as registry_mod
from address_standardizer.audit import StewardshipAuditLedger, StewardshipAuditRecord
from address_standardizer.autocomplete import AutocompleteEngine, _finite_or_none, damerau_levenshtein_distance
from address_standardizer.cache import SQLiteCache, make_cache_key
from address_standardizer.fast_path import (
    _normalize_fast_sec_unit,
    _normalize_fast_street_phrase,
    fast_path_parse,
)
from address_standardizer.models import StandardizedAddress
from address_standardizer.registry import (
    CorporateRegistryEntry,
    CorporateRiskFlag,
    RegistryCategory,
    _contains_token_run,
    can_safely_merge_corporate_entities,
    evaluate_corporate_risk,
    lookup_corporate_registry,
)
from address_standardizer.spatial import engine as engine_mod
from address_standardizer.spatial.engine import SpatialEngine, get_default_spatial_engine
from address_standardizer.spatial.ingestion import (
    _valid_coordinate,
    build_spatial_database,
    calculate_polygon_centroid,
)


def _std(**kw):
    base = dict(
        street1="100 MAIN ST", street2="", city="DENVER", state="CO", postal_code="80202", country="USA",
        normalized_address_key="k", address_status="standardized", raw_street_address="100 Main St", is_us=True,
    )
    base.update(kw)
    return StandardizedAddress(**base)


# --------------------------------------------------------------------------- audit


class TestAuditLedgerBounds:
    def test_unparseable_row_cap_in_environment_falls_back_to_default(self, monkeypatch):
        monkeypatch.setenv("ADDRESS_STANDARDIZER_AUDIT_MAX_ROWS", "lots")
        ledger = StewardshipAuditLedger()
        try:
            assert ledger._max_rows == 100000
        finally:
            ledger._conn.close()

    def test_file_backed_ledger_is_unbounded_and_never_prunes(self, tmp_path):
        ledger = StewardshipAuditLedger(db_path=str(tmp_path / "audit.db"))
        try:
            assert ledger._max_rows is None
            rec = ledger.record(StewardshipAuditRecord(record_id="R1"))
            ledger.record(StewardshipAuditRecord(record_id="R2"))
            assert ledger._inserts_since_prune == 0  # the prune counter is only used by bounded ledgers
            assert ledger.get_record(rec.audit_id) is not None
        finally:
            ledger._conn.close()


# --------------------------------------------------------------------------- cache


class TestSQLiteCacheEdges:
    def test_zip_state_correction_is_part_of_the_key(self):
        plain = make_cache_key("100 Main St", None, "Denver", "CO", "80202", "USA")
        corrected = make_cache_key("100 Main St", None, "Denver", "CO", "80202", "USA", correct_state_from_zip=True)
        assert plain != corrected
        assert "ZIP_STATE" in corrected and "ZIP_STATE" not in plain

    def test_unserialisable_value_is_stored_as_its_string_form(self):
        cache = SQLiteCache()
        cache.set("k", {1, 2})
        assert cache.get("k") == str({1, 2})

    def test_legacy_non_dict_payload_is_returned_as_is(self):
        cache = SQLiteCache()
        with cache._conn:
            cache._conn.execute(
                "INSERT INTO l2_address_cache (cache_key, payload, created_at) VALUES (?, ?, ?)", ("old", "[1, 2, 3]", 0.0)
            )
        assert cache.get("old") == [1, 2, 3]

    def test_payload_without_country_iso3_keeps_the_address_default(self):
        cache = SQLiteCache()
        cache.set("a", _std())
        row = cache._conn.execute("SELECT payload FROM l2_address_cache WHERE cache_key = 'a'").fetchone()
        payload = json.loads(row["payload"])
        payload.pop("country_iso3", None)
        with cache._conn:
            cache._conn.execute("UPDATE l2_address_cache SET payload = ? WHERE cache_key = 'a'", (json.dumps(payload),))
        got = cache.get("a")
        assert isinstance(got, StandardizedAddress)
        assert got.street1 == "100 MAIN ST"
        assert got.country_iso3 == "USA"

    def test_max_entries_zero_disables_eviction(self):
        cache = SQLiteCache(max_entries=0)
        for i in range(5):
            cache.set(f"k{i}", i)
        assert cache.size() == 5
        assert cache.stats()["evictions"] == 0


# --------------------------------------------------------------------------- registry


def _entry(**kw):
    base = dict(
        provider_name="TEST HUB", category=RegistryCategory.COMMERCIAL_REGISTERED_AGENT,
        street_patterns=["1 TEST PLAZA"], city="DENVER", state="CO", postal_code="80202",
    )
    base.update(kw)
    return CorporateRegistryEntry(**base)


@pytest.fixture
def custom_registry(monkeypatch):
    def install(*entries):
        monkeypatch.setattr(registry_mod, "CURATED_CORPORATE_REGISTRY", list(entries))
    return install


class TestRegistryLookupBranches:
    def test_empty_pattern_never_matches(self):
        assert _contains_token_run("", "ANYTHING") is False
        assert _contains_token_run("12 OAK", "112 OAK ST") is False
        assert _contains_token_run("12 OAK", "12 OAK ST") is True

    def test_zip_that_contradicts_the_entry_rules_it_out(self, custom_registry):
        custom_registry(_entry(city=""))
        assert lookup_corporate_registry("1 Test Plaza", state="CO", postal_code="10001") is None
        assert lookup_corporate_registry("1 Test Plaza", state="CO", postal_code="80203") is not None

    def test_entry_without_state_matches_on_city(self, custom_registry):
        custom_registry(_entry(state="", postal_code=""))
        assert lookup_corporate_registry("1 Test Plaza", city="Denver") is not None

    def test_entry_without_city_matches_on_state(self, custom_registry):
        custom_registry(_entry(city="", postal_code=""))
        assert lookup_corporate_registry("1 Test Plaza", state="CO") is not None

    def test_entry_without_postal_code_matches_on_city(self, custom_registry):
        custom_registry(_entry(postal_code="", state=""))
        assert lookup_corporate_registry("1 Test Plaza", city="Denver", postal_code="99999") is not None

    def test_street_match_without_any_jurisdiction_evidence_is_not_a_hit(self, custom_registry):
        custom_registry(_entry(city="", postal_code=""))
        # no state, no city, no ZIP supplied and the text never mentions CO
        assert lookup_corporate_registry("1 Test Plaza") is None

    def test_international_entry_without_city_matches_on_country(self, custom_registry):
        custom_registry(_entry(country="GBR", city="", state="", postal_code="", street_patterns=["1 TEST HOUSE"]))
        assert lookup_corporate_registry("1 Test House", country="GBR") is not None
        assert lookup_corporate_registry("1 Test House", country="FRA") is None


class TestRegistryRiskAndMerge:
    def test_known_non_hub_location_blocks_merge_with_mail_drop_message(self, custom_registry):
        custom_registry(_entry(category=RegistryCategory.VIRTUAL_OFFICE, provider_name="VO CO"))
        a = {"street1": "1 Test Plaza", "city": "Denver", "state": "CO", "postal_code": "80202",
             "building_key": "B1", "normalized_address_key": "N1"}
        b = dict(a, normalized_address_key="N2")
        ok, reason = can_safely_merge_corporate_entities(a, b)
        assert ok is False
        assert reason.startswith("CO_LOCATION_ISOLATION_INVARIANT: Shared virtual office or CMRA mail drop")

    def test_private_residence_object_without_hub_attribute_is_scored_without_error(self):
        obj = SimpleNamespace(is_private_residence=True)
        score, flags = evaluate_corporate_risk(obj)
        assert score == 0.40
        assert flags == [CorporateRiskFlag.RISK_RESIDENTIAL_COMMERCIAL]
        assert not hasattr(obj, "is_registered_agent_hub")

    def test_entry_with_unlisted_category_adds_no_category_flag(self, custom_registry):
        custom_registry(_entry(category="SOMETHING_ELSE", base_risk_score=0.30))
        addr = {"street1": "1 Test Plaza", "street2": "STE 5", "city": "Denver", "state": "CO", "postal_code": "80202",
                "raw_street_address": "1 Test Plaza"}
        score, flags = evaluate_corporate_risk(addr)
        assert score == 0.30
        assert flags == []

    def test_mail_drop_entry_with_pmb_reports_the_cmra_flag_once(self, custom_registry):
        custom_registry(_entry(category=RegistryCategory.MAIL_DROP_CMRA, base_risk_score=0.5))
        addr = {"street1": "1 Test Plaza", "street2": "PMB 12", "city": "Denver", "state": "CO", "postal_code": "80202",
                "raw_street_address": "1 Test Plaza PMB 12"}
        score, flags = evaluate_corporate_risk(addr, {"street1": "1 Test Plaza PMB 12"})
        assert flags.count(CorporateRiskFlag.RISK_CMRA_MAIL_DROP) == 1
        assert score == 0.60


# --------------------------------------------------------------------------- fast path


class TestFastPathEdges:
    def test_descriptive_unit_words_normalise(self):
        assert _normalize_fast_sec_unit("Basement") == "BSMT"
        assert _normalize_fast_sec_unit("Penthouse") == "PH"
        assert _normalize_fast_sec_unit("Front") == "FRNT"

    def test_trailing_descriptive_unit_after_a_street_is_split_off(self):
        assert _normalize_fast_street_phrase("100 Main St Basement") == ("100 MAIN ST", "BSMT")

    def test_country_only_phrase_has_no_street(self):
        assert _normalize_fast_street_phrase(", USA") is None
        assert _normalize_fast_street_phrase("USA") is None

    def test_directional_typos_are_only_healed_with_fuzzy_matching(self):
        assert _normalize_fast_street_phrase("100 Nrth Main St", enable_fuzzy=True) == ("100 N MAIN ST", "")
        assert _normalize_fast_street_phrase("100 Main St Nrth", enable_fuzzy=True) == ("100 MAIN ST N", "")
        # Without fuzzy matching the misspelt directional is treated as ordinary text, which leaves no valid suffix.
        assert _normalize_fast_street_phrase("100 Main St Nrth", enable_fuzzy=False) is None
        assert _normalize_fast_street_phrase("100 Nrth Main St", enable_fuzzy=False) == ("100 NRTH MAIN ST", "")

    def test_exact_directionals_work_without_fuzzy_matching(self):
        assert _normalize_fast_street_phrase("100 N Main St", enable_fuzzy=False) == ("100 N MAIN ST", "")
        assert _normalize_fast_street_phrase("100 Main St N", enable_fuzzy=False) == ("100 MAIN ST N", "")

    def test_numbered_street_beyond_999_is_kept_verbatim(self):
        assert _normalize_fast_street_phrase("100 1000th St") == ("100 1000TH ST", "")

    def test_street_that_is_only_the_city_state_zip_tail_falls_through(self):
        for street in ("Denver CO 80202", "Denver, CO 80202"):
            assert fast_path_parse(street, city="Denver", state="CO", postal_code="80202") is None

    def test_comma_form_respects_enable_fuzzy_for_zip_and_city_healing(self):
        healed = fast_path_parse("100 Main St, Denver, CO 08022", enable_fuzzy=True)
        strict = fast_path_parse("100 Main St, Denver, CO 08022", enable_fuzzy=False)
        assert healed.postal_code == "80022"  # transposed digits repaired
        assert strict.postal_code == "08022"  # taken verbatim
        assert strict.city == "DENVER"


# --------------------------------------------------------------------------- autocomplete


@pytest.fixture
def ac():
    e = AutocompleteEngine(seed=False)
    e.index_address("100 Main St", "Denver", "CO", "80202", latitude=39.74, longitude=-104.99)
    e.index_address("200 Oak Ave", "Austin", "TX", "78701", latitude=30.26, longitude=-97.74)
    e.index_address("5 北京 Rd", "Beijing", "CN", "100000")
    return e


class TestAutocompleteEdges:
    def test_distance_helpers(self):
        assert damerau_levenshtein_distance("abcd", "ab") == 2  # length gap of 2 is reported directly
        assert damerau_levenshtein_distance("abc", "acb") == 1
        assert _finite_or_none("x") is None
        assert _finite_or_none(float("nan")) is None
        assert _finite_or_none("3") == 3.0

    def test_unit_suffix_in_query_falls_back_to_the_base_address(self, ac):
        assert [s.street1 for s in ac.search("100 main st apt 5")] == ["100 MAIN ST"]

    def test_fallback_still_tolerates_a_typo_in_the_base_address(self, ac):
        assert [s.street1 for s in ac.search("100 mian st apt 5")] == ["100 MAIN ST"]
        assert ac.search("100 mian st apt 5", typo_tolerance=False) == []

    def test_unmatched_multi_token_query_without_unit_returns_nothing(self, ac):
        assert ac.search("zzz yyy xxx") == []
        assert ac.search("apt 5 zzz") == []  # unit word first: nothing before it to fall back to

    def test_radius_in_miles_is_converted_and_filters_far_records(self, ac):
        near = dict(client_lat=39.74, client_lon=-104.99)
        assert [s.street1 for s in ac.search("100 main", radius_miles=1, **near)] == ["100 MAIN ST"]
        # Austin is ~1,200 km away: inside a 5,000 km radius but outside 100 km / 1 mile
        assert ac.search("200 oak", radius_km=100, **near) == []
        assert ac.search("200 oak", radius_miles=1, **near) == []
        assert [s.street1 for s in ac.search("200 oak", radius_km=5000, **near)] == ["200 OAK AVE"]

    def test_non_latin_tokens_are_indexed_without_an_ascii_fold(self, ac):
        assert [s.street1 for s in ac.search("北京")] == ["5 北京 RD"]

    def test_connect_reference_index_reads_known_units_and_survives_corrupt_json(self, tmp_path):
        from address_standardizer.offline_index import OfflineReferenceIndex

        idx = OfflineReferenceIndex(db_path=str(tmp_path / "ref.db"))
        idx.insert_record("1 UNIT PL|DENVER", "B1", street1="1 UNIT PL", city="DENVER", state="CO",
                          postal_code="80202", latitude=39.7, longitude=-104.9, known_units=["STE 100", "STE 200"])
        idx.insert_record("2 BAD PL|DENVER", "B2", street1="2 BAD PL", city="DENVER", state="CO",
                          postal_code="80202", latitude=39.7, longitude=-104.9)
        with idx._lock, idx._conn:
            idx._conn.execute("UPDATE rooftop_reference SET known_units = 'not json' WHERE street1 = '2 BAD PL'")
        engine = AutocompleteEngine(seed=False)
        assert engine.connect_reference_index(idx) >= 2  # the index also holds its own seed rows
        assert engine.connect_reference_index(idx) == 0  # already indexed
        by_street = {r["street1"]: r["known_units"] for r in engine._records}
        assert by_street["1 UNIT PL"] == ["STE 100", "STE 200"]
        assert by_street["2 BAD PL"] == []

    def test_connect_reference_index_defaults_to_the_shared_index(self):
        engine = AutocompleteEngine(seed=False)
        assert engine.connect_reference_index() >= 0
        from address_standardizer.offline_index import get_default_offline_index

        with get_default_offline_index()._lock:
            total = get_default_offline_index()._conn.execute("SELECT COUNT(*) FROM rooftop_reference").fetchone()[0]
        assert len(engine._records) <= total


# --------------------------------------------------------------------------- spatial engine


@pytest.fixture
def seeded():
    e = SpatialEngine(seed=True)
    yield e
    e.close()


class TestSpatialEngineEdges:
    def test_connection_is_rebuilt_after_a_fork_style_pid_change(self, tmp_path):
        eng = SpatialEngine(db_path=str(tmp_path / "s.db"), seed=True)
        before = eng.count()
        eng._pid = -1  # simulate a forked child that inherited the parent's connection
        assert eng.count() == before  # reconnected to the same file; nothing re-seeded
        assert eng._pid == os.getpid()
        eng.close()

    def test_forked_memory_engine_is_reseeded(self):
        eng = SpatialEngine(seed=True)
        before = eng.count()
        eng._pid = -1
        assert eng.count() == before  # a fresh in-memory database is seeded again
        eng.close()

    def test_zero_limit_returns_nothing(self, seeded):
        assert seeded.query_bounding_box(-180, -90, 180, 90, limit=0) == []

    def test_points_without_metadata_json_still_load(self, seeded):
        seeded.insert_point("K1", "B1", 10.0, 10.0)
        with seeded._lock, seeded._conn:
            seeded._conn.execute("UPDATE spatial_points SET metadata_json = NULL WHERE address_key = 'K1'")
        res = seeded.query_bounding_box(9.9, 9.9, 10.1, 10.1)
        assert len(res) == 1 and res[0].metadata == {}

    def test_radius_query_around_a_pole_covers_all_longitudes(self):
        eng = SpatialEngine(seed=False)
        eng.insert_point("P1", "B1", 89.95, 120.0)
        eng.insert_point("P2", "B2", 89.95, -60.0)
        found = eng.query_radius(lon=0.0, lat=89.99, radius_meters=20000.0)
        assert sorted(round(r.longitude) for r in found) == [-60, 120]
        eng.close()

    def test_radius_query_wraps_across_the_antimeridian(self):
        eng = SpatialEngine(seed=False)
        eng.insert_point("E1", "B1", 0.0, 179.995)
        eng.insert_point("W1", "B2", 0.0, -179.995)
        eng.insert_point("FAR", "B3", 0.0, 0.0)
        found = eng.query_radius(lon=179.99, lat=0.0, radius_meters=5000.0)
        assert sorted(r.longitude for r in found) == [-179.995, 179.995]
        eng.close()

    def test_radius_query_drops_box_corners_outside_the_circle(self):
        eng = SpatialEngine(seed=False)
        eng.insert_point("IN", "B1", 0.004, 0.004)
        eng.insert_point("CORNER", "B2", 0.0085, 0.0085)  # inside the bounding box, ~1.3 km from the centre
        found = eng.query_radius(lon=0.0, lat=0.0, radius_meters=1000.0)
        assert [r.latitude for r in found] == [0.004]
        eng.close()

    def test_pipe_key_with_country_segment_resolves_by_exact_key(self):
        eng = SpatialEngine(seed=False)
        eng.insert_point("1 X ST||TORONTO|ON|M5V 2T6|CAN", "B", 43.64, -79.38)
        res = eng.resolve("1 X ST||TORONTO|ON|M5V 2T6|CAN")
        assert res.stage == 1 and res.latitude == pytest.approx(43.64)
        eng.close()

    def test_pipe_key_without_a_country_segment_resolves_by_exact_key_only(self):
        eng = SpatialEngine(seed=False)
        eng.insert_point("1 X ST||DENVER|CO|80202", "B", 39.7, -104.9)
        assert eng.resolve("1 X ST||DENVER|CO|80202").stage == 1
        assert eng.resolve("9 Y ST||DENVER|CO|80202||").precision == "UNRESOLVED"  # blank country segment, unknown key
        eng.close()

    def test_connection_rebuild_is_skipped_when_another_thread_already_did_it(self):
        eng = SpatialEngine(seed=False)
        real_lock = eng._lock

        class RebuildingLock:
            """Lets a 'concurrent' thread finish the reconnect between the unlocked check and the locked re-check."""

            def __enter__(self_inner):
                real_lock.acquire()
                eng._pid = os.getpid()

            def __exit__(self_inner, *exc):
                real_lock.release()
                return False

        conn_before = eng._real_conn
        eng._pid = -1
        eng._lock = RebuildingLock()
        assert eng._conn is conn_before  # no second connection was opened
        eng.close()

    def test_explicit_is_us_flag_gates_postal_centroid_matching(self, seeded):
        us = seeded.resolve({"postal_code": "94105", "is_us": True})
        non_us = seeded.resolve({"postal_code": "94105", "is_us": False})
        assert us.stage == 3 and us.precision == "POSTAL_CENTROID"
        assert non_us.precision == "UNRESOLVED"

    def test_unknown_parcel_falls_through_to_street_interpolation(self, seeded):
        res = seeded.resolve({"parcel_id": "NO-SUCH-PARCEL", "street1": "250 Broadway", "postal_code": "10007"})
        assert res.stage == 2 and res.precision == "RANGE_INTERPOLATED"

    def test_street_without_house_number_skips_interpolation(self, seeded):
        res = seeded.resolve({"street1": "Broadway", "postal_code": "10007"})
        assert res.stage == 3

    def test_house_number_outside_every_segment_range_falls_back_to_postal_centroid(self, seeded):
        res = seeded.resolve({"street1": "999 Broadway", "postal_code": "10007"})
        assert res.stage == 3

    def test_close_without_a_connection_is_a_no_op(self):
        eng = SpatialEngine(seed=False)
        eng._conn.close()
        eng._conn = None
        eng.close()  # must not raise


class TestDefaultSpatialEngine:
    def test_engine_is_loaded_from_a_data_directory_under_the_working_directory(self, tmp_path, monkeypatch):
        (tmp_path / "data").mkdir()
        db = tmp_path / "data" / "spatial_index.db"
        built = SpatialEngine(db_path=str(db), seed=False)
        built.insert_point("ONLY|KEY", "B", 1.0, 2.0)
        built.close()
        monkeypatch.delenv("SPATIAL_DB_PATH", raising=False)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(engine_mod, "_DEFAULT_SPATIAL_ENGINE", None)
        eng = get_default_spatial_engine()
        assert eng.count() == 1  # the on-disk database was used and not seeded
        assert eng.has_address_key("only|key")
        eng.close()

    def test_losing_the_creation_race_returns_the_winner(self, monkeypatch):
        winner = object()

        class RacingLock:
            def __enter__(self):
                monkeypatch.setattr(engine_mod, "_DEFAULT_SPATIAL_ENGINE", winner)

            def __exit__(self, *exc):
                return False

        monkeypatch.setattr(engine_mod, "_DEFAULT_SPATIAL_ENGINE", None)
        monkeypatch.setattr(engine_mod, "_SPATIAL_ENGINE_LOCK", RacingLock())
        assert get_default_spatial_engine() is winner


# --------------------------------------------------------------------------- spatial ingestion


class TestSpatialIngestionEdges:
    def test_centroid_of_a_ring_crossing_the_antimeridian_is_wrapped_back(self):
        ring = [[179.9, 0.0], [-179.7, 0.0], [-179.7, 1.0], [179.9, 1.0]]
        lon, lat = calculate_polygon_centroid(ring)
        assert lon == pytest.approx(-179.9, abs=1e-4)
        assert lat == pytest.approx(0.5, abs=1e-4)

    @pytest.mark.parametrize("lat,lon", [("north", 1), (None, 1), (1, [2]), (float("nan"), 1), (91, 0), (0, 181)])
    def test_invalid_coordinates_are_rejected(self, lat, lon):
        assert _valid_coordinate(lat, lon) is False

    def test_valid_coordinate_accepts_numeric_strings(self):
        assert _valid_coordinate("39.7", "-104.9") is True

    def test_build_without_source_data_yields_the_seeded_database(self, tmp_path):
        from address_standardizer.spatial.engine import SEED_SPATIAL_POINTS

        eng = build_spatial_database(str(tmp_path / "out.db"))
        try:
            assert eng.count() == len(SEED_SPATIAL_POINTS)
        finally:
            eng.close()
