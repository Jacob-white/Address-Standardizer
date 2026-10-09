"""Pluggable cache backends: the CacheBackend protocol, the Redis backend (against an in-test fake client, no network)
and backend selection through configure_cache / ADDRESS_STANDARDIZER_CACHE_URL."""

import json
import logging
import sys
import types

import pytest

from address_standardizer import cache as cache_mod
from address_standardizer import standardize_address
from address_standardizer.cache import LRUCache, MultiTierCache, SQLiteCache, configure_cache, get_default_cache
from address_standardizer.cache_backends import (
    CacheBackend,
    RedisCacheBackend,
    backend_from_url,
    deserialize_value,
    serialize_value,
)


class FakeRedis:
    """The slice of redis-py the backend uses, backed by a dict. ``fail`` makes every command raise."""

    def __init__(self):
        self.store = {}
        self.ttls = {}
        self.fail = False
        self.calls = 0

    def _check(self):
        self.calls += 1
        if self.fail:
            raise ConnectionError("redis is down")

    def get(self, name):
        self._check()
        value = self.store.get(name)
        return value.encode("utf-8") if isinstance(value, str) else value

    def set(self, name, value, ex=None):
        self._check()
        self.store[name] = value
        self.ttls[name] = ex
        return True

    def delete(self, *names):
        self._check()
        removed = 0
        for name in names:
            if self.store.pop(name, None) is not None:
                removed += 1
        return removed

    def scan_iter(self, match=None, count=None):
        self._check()
        assert match.endswith("*")
        prefix = match[:-1]
        return iter([name for name in list(self.store) if name.startswith(prefix)])


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def fake():
    return FakeRedis()


@pytest.fixture
def backend(fake, clock):
    return RedisCacheBackend(client=fake, prefix="t:", ttl_seconds=60, retry_after=30.0, clock=clock)


@pytest.fixture(autouse=True)
def _restore_default_cache():
    original = cache_mod._DEFAULT_CACHE
    yield
    cache_mod._DEFAULT_CACHE = original


# -- protocol / codec -------------------------------------------------------------------------------------------------


def test_builtin_tiers_and_redis_satisfy_the_protocol(backend):
    assert isinstance(LRUCache(), CacheBackend)
    assert isinstance(SQLiteCache(), CacheBackend)
    assert isinstance(MultiTierCache(), CacheBackend)
    assert isinstance(backend, CacheBackend)


def test_codec_round_trips_standardized_addresses_and_plain_values():
    std = standardize_address("100 Main St", "Ste 4", "New York", "NY", "10001", "USA", use_cache=False)
    payload = serialize_value(std)
    assert json.loads(payload)["__class__"] == "StandardizedAddress"
    back = deserialize_value(payload)
    assert back.as_dict() == std.as_dict()
    assert deserialize_value(serialize_value("text")) == "text"
    assert deserialize_value(serialize_value(None)) is None
    assert deserialize_value(serialize_value(object())).startswith("<object object")
    assert deserialize_value("[1, 2]") == [1, 2]


# -- Redis backend ----------------------------------------------------------------------------------------------------


def test_redis_round_trip_ttl_and_prefix(backend, fake):
    std = standardize_address("100 Main St", None, "New York", "NY", "10001", "USA", use_cache=False)
    assert backend.get("k") is None
    backend.set("k", std)
    assert "t:k" in fake.store and fake.ttls["t:k"] == 60
    assert backend.get("k").as_dict() == std.as_dict()
    stats = backend.stats()
    assert (stats["hits"], stats["misses"], stats["errors"], stats["degraded"]) == (1, 1, 0, False)
    assert stats["hit_rate"] == 0.5 and stats["backend"] == "redis" and stats["size"] is None


def test_redis_str_payload_and_no_ttl(fake, clock):
    b = RedisCacheBackend(client=fake, ttl_seconds=None, clock=clock)
    assert b.ttl_seconds is None
    fake.store[b.prefix + "s"] = serialize_value("v")  # a client with decode_responses=True returns str
    fake.get = lambda name: fake.store.get(name)
    assert b.get("s") == "v"
    b.set("n", 1)
    assert fake.ttls[b.prefix + "n"] is None
    assert RedisCacheBackend(client=fake, ttl_seconds=0).ttl_seconds is None


def test_redis_corrupt_payload_is_a_miss_and_is_deleted(backend, fake):
    fake.store["t:bad"] = b"{not json"
    assert backend.get("bad") is None
    assert "t:bad" not in fake.store


def test_redis_cached_none_counts_as_a_miss(backend):
    backend.set("n", None)
    assert backend.get("n") is None
    assert backend.stats()["hits"] == 0


def test_redis_delete(backend):
    backend.set("k", "v")
    assert backend.delete("k") is True
    assert backend.delete("k") is False


def test_redis_clear_only_touches_own_prefix_and_batches(backend, fake):
    fake.store["other:keep"] = b"1"
    for i in range(1000):  # exactly two full batches, so no remainder batch
        fake.store[f"t:{i}"] = b"1"
    backend.clear()
    assert list(fake.store) == ["other:keep"]
    for i in range(501):  # one full batch plus a remainder
        fake.store[f"t:{i}"] = b"1"
    backend.clear()
    assert list(fake.store) == ["other:keep"]
    backend.clear()  # nothing left under the prefix
    assert list(fake.store) == ["other:keep"]
    assert backend.stats()["hits"] == 0


def test_redis_outage_degrades_to_miss_logs_once_and_recovers(backend, fake, clock, caplog):
    backend.set("k", "v")
    fake.fail = True
    with caplog.at_level(logging.WARNING, logger="address_standardizer.cache_backends"):
        assert backend.get("k") is None  # fails, logged
        calls_after_first_failure = fake.calls
        clock.now += 1
        assert backend.get("k") is None  # paused: Redis not touched
        backend.set("k", "x")
        assert backend.delete("k") is False
        backend.clear()
        assert fake.calls == calls_after_first_failure
        assert backend.stats()["degraded"] is True  # clear() reset the counters; the pause is still active
    assert len([r for r in caplog.records if "Redis cache" in r.getMessage()]) == 1
    clock.now += 31  # retry window elapsed; still down -> a second failure, not logged again
    fake.fail = True
    assert backend.get("k") is None
    assert len([r for r in caplog.records if "Redis cache" in r.getMessage()]) == 1
    assert backend.stats()["errors"] == 1
    clock.now += 31
    fake.fail = False
    assert backend.get("k") == "v"  # recovered


@pytest.mark.parametrize("action", ["set", "delete", "clear"])
def test_redis_every_command_failure_is_swallowed(backend, fake, action):
    fake.fail = True
    if action == "set":
        backend.set("k", "v")
    elif action == "delete":
        assert backend.delete("k") is False
    else:
        backend.clear()
    stats = backend.stats()
    assert stats["errors"] == 1 and stats["degraded"] is True


def test_redis_constructor_requires_url_or_client():
    with pytest.raises(ValueError):
        RedisCacheBackend()


def test_redis_client_built_lazily_from_url(monkeypatch, fake):
    seen = {}

    class _Redis:
        @staticmethod
        def from_url(url, **kwargs):
            seen["url"], seen["kwargs"] = url, kwargs
            return fake

    monkeypatch.setitem(sys.modules, "redis", types.SimpleNamespace(Redis=_Redis))
    b = RedisCacheBackend("redis://cache:6379/2", socket_timeout=0.5)
    assert seen == {}  # constructing never connects
    b.set("k", "v")
    b.get("k")
    assert seen["url"] == "redis://cache:6379/2" and seen["kwargs"]["socket_timeout"] == 0.5


def test_redis_missing_package_degrades_instead_of_raising(monkeypatch, caplog):
    monkeypatch.setitem(sys.modules, "redis", None)  # makes "import redis" raise ImportError
    b = RedisCacheBackend("redis://localhost:6379/0")
    with caplog.at_level(logging.WARNING, logger="address_standardizer.cache_backends"):
        assert b.get("k") is None
        b.set("k", "v")
    assert "address-standardizer[redis]" in caplog.text
    assert b.stats()["errors"] == 1


# -- selection --------------------------------------------------------------------------------------------------------


def test_backend_from_url():
    for url in ("redis://h:1/0", "rediss://h:1/0", "unix:///tmp/redis.sock"):
        assert isinstance(backend_from_url(url), RedisCacheBackend)
    with pytest.raises(ValueError):
        backend_from_url("memcached://h:11211")


def test_configure_cache_accepts_instance_url_and_env(monkeypatch, backend):
    monkeypatch.delenv(cache_mod.CACHE_URL_ENV, raising=False)
    assert configure_cache(backend=backend)._l2 is backend
    assert isinstance(configure_cache(backend="redis://localhost:6379/0")._l2, RedisCacheBackend)
    assert isinstance(configure_cache()._l2, SQLiteCache)
    monkeypatch.setenv(cache_mod.CACHE_URL_ENV, "redis://localhost:6379/1")
    assert isinstance(configure_cache()._l2, RedisCacheBackend)
    assert isinstance(configure_cache(backend=SQLiteCache())._l2, SQLiteCache)  # explicit backend beats the env var
    monkeypatch.setenv(cache_mod.CACHE_URL_ENV, "bogus://x")
    assert isinstance(configure_cache()._l2, SQLiteCache)  # invalid URL: logged, default kept


def test_default_cache_over_redis_end_to_end_and_survives_outage(backend, fake, clock):
    configure_cache(backend=backend)
    args = ("100 Main St", "Ste 4", "New York", "NY", "10001", "USA")
    first = standardize_address(*args)
    assert any(name.startswith("t:") for name in fake.store)
    get_default_cache()._l1.clear()  # a second process would have an empty L1 but see the same Redis
    second = standardize_address(*args)
    assert second.as_dict() == first.as_dict()
    stats = get_default_cache().get_stats()
    assert stats["l2_backend"] == "redis" and stats["l2"]["hits"] == 1
    fake.fail = True
    get_default_cache()._l1.clear()
    assert standardize_address(*args).as_dict() == first.as_dict()  # outage: recomputed, never an error
    assert set(get_default_cache().stats()) == set(get_default_cache().get_stats())


def test_multi_tier_get_does_not_hold_a_lock_across_l2(backend):
    cache = MultiTierCache(l2=backend)
    cache.set("k", "v")
    assert cache.get("k") == "v"
    cache._l1.clear()
    assert cache.get("k") == "v"  # served from L2 and promoted
    assert cache._l1.get("k") == "v"
