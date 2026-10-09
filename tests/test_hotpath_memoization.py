"""Behaviour-preservation tests for the hot-path optimisations (registry lookup memo, token-run regex cache,
cache-key construction). No timing assertions."""

import dataclasses

import pytest

from address_standardizer import registry
from address_standardizer.cache import make_cache_key


def _reference_key(street1, street2, city, state, postal_code, country):
    """The documented key format (stripped, upper-cased, backslash and pipe escaped); persisted L2/Redis keys depend on it."""
    parts = [
        (str(street1).strip().upper() if street1 is not None else ""),
        (str(street2).strip().upper() if street2 is not None else ""),
        (str(city).strip().upper() if city is not None else ""),
        (str(state).strip().upper() if state is not None else ""),
        (str(postal_code).strip().upper() if postal_code is not None else ""),
        (str(country).strip().upper() if country is not None and str(country).strip() else "USA"),
    ]
    parts = [p.replace("\\", "\\\\").replace("|", "\\|") for p in parts]
    return "|".join(parts)


@pytest.mark.parametrize(
    "fields",
    [
        ("100 Main St", "Ste 4", "New York", "NY", "10001", "USA"),
        (None, None, None, None, None, None),
        ("  a|b  ", "c\\d", "e|", "|", " ", "   "),
        (12, 3.5, b"x".decode(), "ny", 10001, ""),
        ("ул. Тверская 12", "", "Москва", "", "101000", "rus"),
    ],
)
def test_make_cache_key_format_is_stable(fields):
    assert make_cache_key(*fields) == _reference_key(*fields)


def test_token_run_matching_semantics():
    assert registry._contains_token_run("1209 N ORANGE", "AT 1209 N ORANGE ST") is True
    assert registry._contains_token_run("1209 N ORANGE", "AT 11209 N ORANGE ST") is False  # substring, not a token run
    assert registry._contains_token_run("1209 N ORANGE", "NOTHING HERE") is False  # rejected by the substring test
    assert registry._contains_token_run("", "ANYTHING") is False
    assert registry._token_run_regex("A.B") is registry._token_run_regex("A.B")  # compiled once, metacharacters escaped
    assert registry._contains_token_run("A.B", "XA.B") is False
    assert registry._contains_token_run("A.B", "A.B") is True


def test_registry_lookup_is_memoized_and_equivalent_to_uncached():
    registry._LOOKUP_MEMO.clear()
    args = dict(street1="1209 N Orange St", city="Wilmington", state="DE", postal_code="19801")
    first = registry.lookup_corporate_registry(**args)
    assert first is not None
    assert registry.lookup_corporate_registry(**args) is first  # memo hit returns the identical entry
    assert registry._lookup_corporate_registry_uncached(**args) is first
    assert registry.lookup_corporate_registry("1 Nowhere Rd") is None  # a miss is memoized as None
    assert registry.lookup_corporate_registry("1 Nowhere Rd") is None


def test_registry_memo_is_dropped_when_registry_changes(monkeypatch):
    entry = registry.CURATED_CORPORATE_REGISTRY[0]
    registry.lookup_corporate_registry(street1=entry.street_patterns[0])  # fills the memo for the real registry
    replacement = [dataclasses.replace(entry, provider_name="REPLACED")]
    monkeypatch.setattr(registry, "CURATED_CORPORATE_REGISTRY", replacement)  # a different list object
    assert registry.lookup_corporate_registry(street1="1 Nowhere Rd") is None
    assert registry._LOOKUP_MEMO_OWNER[0] is replacement
    replacement.append(dataclasses.replace(entry, provider_name="ADDED", street_patterns=["ZZZ UNIQUE PLAZA"]))
    registry.lookup_corporate_registry(street1="1 Zzz Unique Plaza", state=entry.state)  # same list object, new length
    assert registry._LOOKUP_MEMO_OWNER[1] == 2


def test_registry_memo_is_bounded(monkeypatch):
    monkeypatch.setattr(registry, "_LOOKUP_MEMO_MAX", 3)
    registry._LOOKUP_MEMO.clear()
    for i in range(10):
        registry.lookup_corporate_registry(street1=f"{i} Some Road")
    assert len(registry._LOOKUP_MEMO) <= 3
