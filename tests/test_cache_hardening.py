"""Cache keys must separate every input that changes the result; the L2 cache must never return junk."""

import json

from address_standardizer import standardize_address
from address_standardizer.cache import MultiTierCache, SQLiteCache, make_cache_key


def test_separator_inside_a_field_cannot_collide():
    assert make_cache_key("1 A", "", "X|Y", "NY", "1", "") != make_cache_key("1 A", "", "X", "Y|NY", "1", "")
    assert make_cache_key("1 A|", "B") != make_cache_key("1 A", "|B")


def test_vacancy_override_is_part_of_the_key_and_result():
    plain = standardize_address("77 Quiet Ln", "", "Albany", "NY", "12207")
    flagged = standardize_address("77 Quiet Ln", "", "Albany", "NY", "12207", is_vacant=True)
    again = standardize_address("77 Quiet Ln", "", "Albany", "NY", "12207")
    assert flagged.vacant is True
    assert plain.vacant is False
    assert again.vacant is False


def test_l2_unreadable_payload_is_a_miss_and_is_removed():
    cache = MultiTierCache()
    stale = json.dumps({"__class__": "StandardizedAddress", "street1": "x"})  # missing required fields
    with cache._l2._conn:
        cache._l2._conn.execute(
            "INSERT OR REPLACE INTO l2_address_cache(cache_key, payload) VALUES('old', ?)", (stale,)
        )
    assert cache.get("old") is None
    left = cache._l2._conn.execute("SELECT count(*) FROM l2_address_cache WHERE cache_key='old'").fetchone()[0]
    assert left == 0


def test_l2_generic_values_round_trip_with_their_type():
    cache = SQLiteCache()
    for key, value in [("s", "123"), ("i", 123), ("d", {"a": 1}), ("l", [1, 2])]:
        cache.set(key, value)
        assert cache.get(key) == value
        assert type(cache.get(key)) is type(value)


def test_l2_eviction_prefers_least_recently_used():
    cache = SQLiteCache(max_entries=3)
    for key in "abc":
        cache.set(key, key)
    assert cache.get("a") == "a"  # touch a
    cache.set("d", "d")
    assert cache.get("a") == "a"
    assert cache.get("b") is None


def test_l2_eviction_is_correct_even_with_a_frozen_clock(monkeypatch):
    """A coarse clock (Windows ticks ~16 ms) must not make a write and a touch tie and evict the wrong entry."""
    import address_standardizer.cache as cache_mod

    monkeypatch.setattr(cache_mod.time, "time", lambda: 1000.0)
    cache = SQLiteCache(max_entries=3)
    for key in "abc":
        cache.set(key, key)
    assert cache.get("a") == "a"  # touch a: now the most recently used
    cache.set("d", "d")
    assert cache.get("a") == "a"
    assert cache.get("b") is None
    assert cache._stamp() > 1000.0  # stamps keep increasing while the clock does not
