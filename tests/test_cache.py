"""
Tests for Multi-Tier Reference Caching Architecture.
=====================================================
"""

import json
from unittest.mock import patch
from address_standardizer.models import StandardizedAddress
from address_standardizer.cache import (
    make_cache_key,
    LRUCache,
    SQLiteCache,
    MultiTierCache,
    get_default_cache,
    configure_cache,
    clear_cache,
    get_cache_stats,
)


class TestLRUCache:
    def test_lru_basic_ops_and_stats(self):
        cache = LRUCache(maxsize=3)
        assert cache.size() == 0

        # Initial stats
        stats = cache.stats()
        assert stats["size"] == 0
        assert stats["hit_rate"] == 0.0

        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.size() == 3

        # Hit
        assert cache.get("a") == 1
        # Miss
        assert cache.get("d") is None

        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

        # Overwrite key
        cache.set("a", 10)
        assert cache.get("a") == 10

        # Eviction of LRU (since 'a' was accessed, 'b' is oldest)
        cache.set("d", 4)
        assert cache.get("b") is None
        assert cache.get("a") == 10
        assert cache.get("c") == 3
        assert cache.get("d") == 4
        assert cache.stats()["evictions"] == 1

        # Delete
        assert cache.delete("c") is True
        assert cache.delete("nonexistent") is False
        assert cache.size() == 2

        # Clear
        cache.clear()
        assert cache.size() == 0
        assert cache.stats()["hits"] == 0


class TestSQLiteCache:
    def test_sqlite_cache_types_and_lifecycle(self, tmp_path):
        db_path = str(tmp_path / "test_cache.db")
        cache = SQLiteCache(db_path=db_path)
        assert cache.size() == 0

        # StandardizedAddress object caching
        addr = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St",
            is_us=True,
        )
        addr.confidence_score = 0.9950
        addr.routing_tier = "AUTO_PASS"
        addr.failure_reason_codes = ["WARN_CRA_HUB_DETECTED"]

        cache.set("addr_1", addr)
        assert cache.size() == 1

        retrieved = cache.get("addr_1")
        assert isinstance(retrieved, StandardizedAddress)
        assert retrieved.street1 == "100 WALL ST"
        assert retrieved.confidence_score == 0.9950
        assert retrieved.routing_tier == "AUTO_PASS"
        assert retrieved.failure_reason_codes == ["WARN_CRA_HUB_DETECTED"]

        # Primitive and dict types
        cache.set("dict_1", {"key": "value"})
        assert cache.get("dict_1") == {"key": "value"}

        cache.set("num_1", 42)
        assert cache.get("num_1") == 42

        cache.set("str_1", "raw string")
        assert cache.get("str_1") == "raw string"

        # Non-JSON payload handling
        cache._conn.execute("INSERT OR REPLACE INTO l2_address_cache (cache_key, payload) VALUES (?, ?)", ("raw_bad_json", "{bad json"))
        assert cache.get("raw_bad_json") == "{bad json"

        # Miss
        assert cache.get("missing_key") is None

        # Stats
        stats = cache.stats()
        assert stats["size"] >= 4
        assert stats["hits"] >= 4
        assert stats["misses"] == 1
        assert stats["hit_rate"] > 0

        # Delete
        assert cache.delete("dict_1") is True
        assert cache.delete("nonexistent") is False

        # Clear
        cache.clear()
        assert cache.size() == 0

    def test_sqlite_pragma_fallback(self):
        with patch("sqlite3.connect") as mock_conn:
            mock_inst = mock_conn.return_value
            mock_inst.execute.side_effect = [Exception("Pragma failed"), None, None]
            c = SQLiteCache()
            assert c is not None

    def test_sqlite_cache_pid_reconnection(self, tmp_path):
        db_path = str(tmp_path / "fork_cache.db")
        cache = SQLiteCache(db_path=db_path)
        cache._pid = 0
        conn = cache._get_conn()
        assert conn is not None
        assert cache._pid != 0

    def test_sqlite_cache_with_audit_and_cascade(self, tmp_path):
        from address_standardizer.audit import StewardshipAuditRecord, get_audit_ledger
        from address_standardizer.cascade import CascadeResult

        db_path = str(tmp_path / "metadata_cache.db")
        cache = SQLiteCache(db_path=db_path)

        audit_rec = StewardshipAuditRecord(
            record_id="REC-TEST",
            action_type="AUTO_PASS",
            confidence_score=0.98,
        )
        cascade_res = CascadeResult(
            latitude=37.7749,
            longitude=-122.4194,
            precision="CONFIRMED_ROOFTOP",
            accuracy_radius_meters=5.0,
            source="dpv",
            stage=1,
            census_tract="06075010100",
        )

        addr = StandardizedAddress(
            street1="100 MARKET ST",
            street2="STE 300",
            city="SAN FRANCISCO",
            state="CA",
            postal_code="94105",
            country="USA",
            normalized_address_key="100 MARKET ST|STE 300|SAN FRANCISCO|CA|94105|USA",
            address_status="standardized",
            raw_street_address="100 Market St, Ste 300",
            is_us=True,
        )
        addr.audit_record = audit_rec
        addr.cascade_result = cascade_res

        from address_standardizer.models import SpatialResolutionResult
        spatial_res = SpatialResolutionResult(
            latitude=37.7749,
            longitude=-122.4194,
            precision="CONFIRMED_ROOFTOP",
            accuracy_radius_meters=3.0,
            stage=1,
            source="OPENADDRESSES",
            h3_res10="8a226204db27fff",
        )
        addr.spatial_result = spatial_res

        cache.set("addr_full", addr)

        retrieved = cache.get("addr_full")
        assert retrieved is not None
        assert retrieved.audit_record is not None
        assert retrieved.audit_record.record_id == "REC-TEST"
        assert retrieved.cascade_result is not None
        assert retrieved.cascade_result.latitude == 37.7749
        assert retrieved.spatial_result is not None
        assert retrieved.spatial_result.latitude == 37.7749
        assert retrieved.country_iso3 == "USA"

        ledger = get_audit_ledger()
        stored_rec = ledger.record(audit_rec)

        d = addr.as_dict(include_metadata=True)
        d["__class__"] = "StandardizedAddress"
        d["audit_id"] = stored_rec.audit_id
        d.pop("audit_record_payload", None)
        d["cascade"] = cascade_res.as_dict()
        d.pop("cascade_result_payload", None)
        d["spatial_result"] = spatial_res.as_dict()
        d.pop("spatial_result_payload", None)
        d["country_iso3"] = "USA"

        cache._conn.execute(
            "INSERT OR REPLACE INTO l2_address_cache (cache_key, payload) VALUES (?, ?)",
            ("addr_fallbacks", json.dumps(d)),
        )

        retrieved2 = cache.get("addr_fallbacks")
        assert retrieved2 is not None
        assert retrieved2.audit_record is not None
        assert retrieved2.audit_record.audit_id == stored_rec.audit_id
        assert retrieved2.cascade_result is not None
        assert retrieved2.cascade_result.latitude == 37.7749
        assert retrieved2.spatial_result is not None
        assert retrieved2.spatial_result.latitude == 37.7749


class TestMultiTierCache:
    def test_multitier_promotion_and_flow(self):
        cache = MultiTierCache(l1_maxsize=2)
        assert cache.is_enabled() is True

        cache.set("k1", "val1")
        # In L1 and L2
        assert cache.get("k1") == "val1"

        # Fill L1 to force eviction into L2
        cache.set("k2", "val2")
        cache.set("k3", "val3")  # k1 evicted from L1

        assert cache._l1.get("k1") is None  # evicted from L1
        # Retrieval from L2 promotes back to L1
        assert cache.get("k1") == "val1"
        assert cache._l1.get("k1") == "val1"  # back in L1

        # Miss on both
        assert cache.get("unknown") is None

        # Delete and clear
        assert cache.delete("k1") is True
        assert cache.get("k1") is None

        cache.clear()
        assert cache.get("k2") is None

    def test_multitier_disable_toggle(self):
        cache = MultiTierCache()
        cache.disable()
        assert cache.is_enabled() is False

        cache.set("k1", "val1")
        assert cache.get("k1") is None

        cache.enable()
        assert cache.is_enabled() is True
        cache.set("k1", "val1")
        assert cache.get("k1") == "val1"

    def test_multitier_stats(self):
        cache = MultiTierCache()
        stats = cache.get_stats()
        assert stats["enabled"] is True
        assert "l1" in stats
        assert "l2" in stats
        assert stats["total_lookups"] == 0

        cache.set("k1", "v1")
        cache.get("k1")
        cache.get("k_miss")

        stats2 = cache.get_stats()
        assert stats2["total_lookups"] == 2
        assert stats2["total_hits"] == 1
        assert stats2["overall_hit_rate"] == 0.5


class TestCacheGlobalControls:
    def test_make_cache_key(self):
        k = make_cache_key(" 100 Main St ", "Ste 100", " New York ", "ny", "10005", "usa")
        assert k == "100 MAIN ST|STE 100|NEW YORK|NY|10005|USA"

        k_default = make_cache_key()
        assert k_default == "|||||USA"

        k_nofuzzy = make_cache_key(" 100 Main St ", enable_fuzzy=False)
        assert k_nofuzzy == "100 MAIN ST|||||USA|NO_FUZZY"

    def test_global_cache_configuration(self):
        def_cache = get_default_cache()
        assert isinstance(def_cache, MultiTierCache)

        cfg = configure_cache(enabled=True, l1_maxsize=1000)
        assert cfg.is_enabled() is True
        assert cfg._l1.maxsize == 1000

        cfg.set("global_test", 123)
        assert cfg.get("global_test") == 123

        st = get_cache_stats()
        assert st["enabled"] is True

        clear_cache()
        assert cfg.get("global_test") is None
