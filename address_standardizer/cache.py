"""
Multi-Tier Reference Caching Architecture.
==========================================
Implements high-performance multi-tier caching (L1 in-process LRU + L2 embedded persistent SQLite)
with sub-millisecond point lookups and zero external service dependencies.

Topology:
  L1: Thread-safe in-process LRU cache (50,000 capacity, < 0.001 ms latency)
  L2: Embedded SQLite key-value store with WAL mode (sub-0.050 ms latency)
"""

import json
import sqlite3
import threading
import time
from collections import OrderedDict
from typing import Dict, Any, Optional


def make_cache_key(
    street1: Optional[str] = None,
    street2: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    country: Optional[str] = None,
    enable_fuzzy: bool = True,
    enable_geocoding: bool = False,
    allow_locality: bool = False,
    is_vacant: Optional[bool] = None,
    correct_state_from_zip: bool = False,
    **kwargs: Any,
) -> str:
    """Computes a normalized cache key from input address components.

    Field values are escaped so that a separator inside one field cannot make two different addresses collide,
    and per-call overrides that change the result (``is_vacant``/``vacant``) are part of the key.
    """
    parts = [
        (str(street1).strip().upper() if street1 is not None else ""),
        (str(street2).strip().upper() if street2 is not None else ""),
        (str(city).strip().upper() if city is not None else ""),
        (str(state).strip().upper() if state is not None else ""),
        (str(postal_code).strip().upper() if postal_code is not None else ""),
        (str(country).strip().upper() if country is not None and str(country).strip() else "USA"),
    ]
    parts = [p.replace("\\", "\\\\").replace("|", "\\|") for p in parts]
    vacant = is_vacant if is_vacant is not None else kwargs.get("vacant")
    if vacant is not None:
        parts.append("VACANT" if vacant else "NOT_VACANT")
    if correct_state_from_zip:
        parts.append("ZIP_STATE")
    if not enable_fuzzy:
        parts.append("NO_FUZZY")
    if enable_geocoding:
        parts.append("GEOCODE")
    if allow_locality:
        parts.append("ALLOW_LOCALITY")
    return "|".join(parts)


class LRUCache:
    """Thread-safe L1 In-Process LRU Cache."""

    def __init__(self, maxsize: int = 50000):
        self.maxsize = max(1, maxsize)
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._hits += 1
                return self._cache[key]
            self._misses += 1
            return None

    def set(self, key: str, value: Any):
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = value
            if len(self._cache) > self.maxsize:
                self._cache.popitem(last=False)
                self._evictions += 1

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0

    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "maxsize": self.maxsize,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": round(hit_rate, 4),
            }


class SQLiteCache:
    """Thread-safe L2 Embedded Persistent Cache using SQLite WAL mode."""

    def __init__(self, db_path: Optional[str] = None, max_entries: int = 50000):
        import os
        self.db_path = db_path or ":memory:"
        self.max_entries = max_entries
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._last_stamp = 0.0
        self._pid = os.getpid()
        self._conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _stamp(self) -> float:
        """A strictly increasing recency stamp. ``time.time()`` ticks in ~16 ms steps on Windows, so a write and an
        immediate read-touch could share a timestamp and LRU eviction would pick the wrong entry; callers hold the lock."""
        self._last_stamp = max(time.time(), self._last_stamp + 1e-6)
        return self._last_stamp

    def _get_conn(self) -> sqlite3.Connection:
        import os
        current_pid = os.getpid()
        if current_pid != self._pid:
            self._pid = current_pid
            self._conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._init_db()
        return self._conn

    def _init_db(self):
        with self._conn:
            try:
                self._conn.execute("PRAGMA journal_mode = WAL;")
                self._conn.execute("PRAGMA synchronous = NORMAL;")
                self._conn.execute("PRAGMA busy_timeout = 30000;")
            except Exception:
                pass
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS l2_address_cache (
                    cache_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at REAL NOT NULL DEFAULT (strftime('%s', 'now'))
                );
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_l2_cache_key ON l2_address_cache(cache_key);"
            )
            try:
                self._conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_l2_created_at ON l2_address_cache(created_at);"
                )
            except Exception:
                pass

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            conn = self._get_conn()
            cur = conn.execute(
                "SELECT payload FROM l2_address_cache WHERE cache_key = ?", (key,)
            )
            row = cur.fetchone()
            if row:
                self._hits += 1
                with conn:  # recency for LRU-style eviction
                    conn.execute("UPDATE l2_address_cache SET created_at = ? WHERE cache_key = ?", (self._stamp(), key))
                try:
                    data = json.loads(row["payload"])
                    if isinstance(data, dict) and data.get("__class__") == "StandardizedAddress":
                        from address_standardizer.models import StandardizedAddress
                        std = StandardizedAddress(
                            street1=data["street1"],
                            street2=data["street2"],
                            city=data["city"],
                            state=data["state"],
                            postal_code=data["postal_code"],
                            country=data["country"],
                            normalized_address_key=data.get("normalized_address_key"),
                            address_status=data["address_status"],
                            raw_street_address=data["raw_street_address"],
                            is_us=data["is_us"],
                            is_private_residence=data.get("is_private_residence", False),
                            building_key=data.get("building_key"),
                            phonetic_key=data.get("phonetic_key"),
                            is_registered_agent_hub=data.get("is_registered_agent_hub", False),
                            rooftop_address=data.get("rooftop_address"),
                        )
                        std.confidence_score = data.get("confidence_score")
                        std.routing_tier = data.get("routing_tier")
                        std.failure_reason_codes = data.get("failure_reason_codes") or []
                        std.rdi = data.get("rdi", "Unknown")
                        std.cmra = data.get("cmra", False)
                        std.is_cmra = data.get("is_cmra", False)
                        std.vacant = data.get("vacant", False)
                        std.is_vacant = data.get("is_vacant", False)
                        std.dpv_footnotes = data.get("dpv_footnotes") or []
                        std.corporate_risk_score = data.get("corporate_risk_score", 0.0)
                        std.corporate_risk_flags = data.get("corporate_risk_flags") or []

                        if data.get("audit_record_payload"):
                            from address_standardizer.audit import StewardshipAuditRecord
                            std.audit_record = StewardshipAuditRecord.from_dict(data["audit_record_payload"])
                        elif data.get("audit_id"):
                            from address_standardizer.audit import get_audit_ledger
                            std.audit_record = get_audit_ledger().get_record(data["audit_id"])

                        if data.get("cascade_result_payload"):
                            from address_standardizer.cascade import CascadeResult
                            c_dict = data["cascade_result_payload"]
                            std.cascade_result = CascadeResult(
                                latitude=c_dict["latitude"],
                                longitude=c_dict["longitude"],
                                precision=c_dict["precision"],
                                accuracy_radius_meters=c_dict["accuracy_radius_meters"],
                                source=c_dict["source"],
                                stage=c_dict["stage"],
                                census_tract=c_dict.get("census_tract"),
                            )
                        elif data.get("cascade") and isinstance(data["cascade"], dict):
                            from address_standardizer.cascade import CascadeResult
                            c_dict = data["cascade"]
                            std.cascade_result = CascadeResult(
                                latitude=c_dict["latitude"],
                                longitude=c_dict["longitude"],
                                precision=c_dict["precision"],
                                accuracy_radius_meters=c_dict["accuracy_radius_meters"],
                                source=c_dict["source"],
                                stage=c_dict["stage"],
                                census_tract=c_dict.get("census_tract"),
                            )

                        if data.get("spatial_result_payload"):
                            from address_standardizer.models import SpatialResolutionResult
                            s_dict = data["spatial_result_payload"]
                            std.spatial_result = SpatialResolutionResult(
                                latitude=s_dict["latitude"],
                                longitude=s_dict["longitude"],
                                precision=s_dict["precision"],
                                accuracy_radius_meters=s_dict["accuracy_radius_meters"],
                                stage=s_dict["stage"],
                                source=s_dict["source"],
                                h3_res10=s_dict["h3_res10"],
                                parcel_id=s_dict.get("parcel_id"),
                                execution_time_ms=s_dict.get("execution_time_ms", 0.0),
                                metadata=s_dict.get("metadata", {}),
                            )
                        elif data.get("spatial_result") and isinstance(data["spatial_result"], dict):
                            from address_standardizer.models import SpatialResolutionResult
                            s_dict = data["spatial_result"]
                            std.spatial_result = SpatialResolutionResult(
                                latitude=s_dict["latitude"],
                                longitude=s_dict["longitude"],
                                precision=s_dict["precision"],
                                accuracy_radius_meters=s_dict["accuracy_radius_meters"],
                                stage=s_dict["stage"],
                                source=s_dict["source"],
                                h3_res10=s_dict["h3_res10"],
                                parcel_id=s_dict.get("parcel_id"),
                                execution_time_ms=s_dict.get("execution_time_ms", 0.0),
                                metadata=s_dict.get("metadata", {}),
                            )

                        if data.get("country_iso3"):
                            std.country_iso3 = data["country_iso3"]

                        return std
                    if isinstance(data, dict) and "__cache_value__" in data:
                        return data["__cache_value__"]
                    return data
                except Exception:
                    # A payload that cannot be rebuilt (older schema, truncated write) is a miss, not a value.
                    self._hits -= 1
                    self._misses += 1
                    with conn:
                        conn.execute("DELETE FROM l2_address_cache WHERE cache_key = ?", (key,))
                    return None
            self._misses += 1
            return None

    def set(self, key: str, value: Any):
        with self._lock:
            from address_standardizer.models import StandardizedAddress
            if isinstance(value, StandardizedAddress):
                d = value.as_dict(include_metadata=True)
                d["__class__"] = "StandardizedAddress"
                if value.audit_record is not None and hasattr(value.audit_record, "as_dict"):
                    d["audit_record_payload"] = value.audit_record.as_dict()
                if value.cascade_result is not None and hasattr(value.cascade_result, "as_dict"):
                    d["cascade_result_payload"] = value.cascade_result.as_dict()
                if value.spatial_result is not None and hasattr(value.spatial_result, "as_dict"):
                    d["spatial_result_payload"] = value.spatial_result.as_dict()
                payload_str = json.dumps(d)
            else:
                # Tag generic values so None / str / int round-trip with their type intact.
                try:
                    payload_str = json.dumps({"__cache_value__": value})
                except (TypeError, ValueError):
                    payload_str = json.dumps({"__cache_value__": str(value)})

            conn = self._get_conn()
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO l2_address_cache (cache_key, payload, created_at) VALUES (?, ?, ?)",
                    (key, payload_str, self._stamp()),
                )
                if self.max_entries and self.max_entries > 0:
                    cur = conn.execute("SELECT COUNT(*) AS cnt FROM l2_address_cache")
                    row = cur.fetchone()
                    cnt = int(row["cnt"]) if row else 0
                    if cnt > self.max_entries:
                        excess = cnt - self.max_entries
                        del_cur = conn.execute(
                            "DELETE FROM l2_address_cache WHERE rowid IN (SELECT rowid FROM l2_address_cache ORDER BY created_at ASC, rowid ASC LIMIT ?)",
                            (excess,),
                        )
                        self._evictions += del_cur.rowcount

    def delete(self, key: str) -> bool:
        with self._lock:
            conn = self._get_conn()
            with conn:
                cur = conn.execute(
                    "DELETE FROM l2_address_cache WHERE cache_key = ?", (key,)
                )
                return cur.rowcount > 0

    def clear(self):
        with self._lock:
            conn = self._get_conn()
            with conn:
                conn.execute("DELETE FROM l2_address_cache")
            self._hits = 0
            self._misses = 0
            self._evictions = 0

    def size(self) -> int:
        with self._lock:
            conn = self._get_conn()
            cur = conn.execute("SELECT COUNT(*) AS cnt FROM l2_address_cache")
            row = cur.fetchone()
            return int(row["cnt"]) if row else 0

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total) if total > 0 else 0.0
            return {
                "size": self.size(),
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": round(hit_rate, 4),
            }


class MultiTierCache:
    """
    Coordinated Multi-Tier Caching System (L1 LRU + L2 SQLite).
    """

    def __init__(
        self,
        l1_maxsize: int = 50000,
        l2_db_path: Optional[str] = None,
        l2_max_entries: int = 50000,
        enabled: bool = True,
    ):
        self._enabled = enabled
        self._l1 = LRUCache(maxsize=l1_maxsize)
        self._l2 = SQLiteCache(db_path=l2_db_path, max_entries=l2_max_entries)
        self._lock = threading.RLock()

    def is_enabled(self) -> bool:
        return self._enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def get(self, key: str) -> Optional[Any]:
        if not self._enabled:
            return None
        with self._lock:
            # 1. Check L1 Cache
            val = self._l1.get(key)
            if val is not None:
                return val

            # 2. Check L2 Cache
            val = self._l2.get(key)
            if val is not None:
                # Promote to L1
                self._l1.set(key, val)
                return val

            return None

    def set(self, key: str, value: Any):
        if not self._enabled:
            return
        with self._lock:
            self._l1.set(key, value)
            self._l2.set(key, value)

    def delete(self, key: str) -> bool:
        with self._lock:
            d1 = self._l1.delete(key)
            d2 = self._l2.delete(key)
            return d1 or d2

    def clear(self):
        with self._lock:
            self._l1.clear()
            self._l2.clear()

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            l1_s = self._l1.stats()
            l2_s = self._l2.stats()
            total_lookups = l1_s["hits"] + l1_s["misses"]
            total_hits = l1_s["hits"] + l2_s["hits"]
            overall_rate = (total_hits / total_lookups) if total_lookups > 0 else 0.0
            return {
                "enabled": self._enabled,
                "l1": l1_s,
                "l2": l2_s,
                "total_lookups": total_lookups,
                "total_hits": total_hits,
                "overall_hit_rate": round(overall_rate, 4),
            }


_DEFAULT_CACHE = MultiTierCache()


def get_default_cache() -> MultiTierCache:
    """Returns the default MultiTierCache instance."""
    return _DEFAULT_CACHE


def configure_cache(
    enabled: bool = True,
    l1_maxsize: int = 50000,
    l2_db_path: Optional[str] = None,
    l2_max_entries: int = 50000,
) -> MultiTierCache:
    """Configures global caching parameters."""
    global _DEFAULT_CACHE
    _DEFAULT_CACHE = MultiTierCache(
        l1_maxsize=l1_maxsize,
        l2_db_path=l2_db_path,
        l2_max_entries=l2_max_entries,
        enabled=enabled,
    )
    return _DEFAULT_CACHE


def clear_cache():
    """Clears L1 and L2 caches."""
    _DEFAULT_CACHE.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Returns statistics for L1 and L2 caches."""
    return _DEFAULT_CACHE.get_stats()
