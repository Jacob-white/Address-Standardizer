"""alternatives=N: next-best readings of ambiguous input (deterministic, bounded, side-effect free)."""

from address_standardizer import standardize_address
from address_standardizer.audit import get_audit_ledger


def alts(**kwargs):
    kwargs.setdefault("finalize", False)
    return standardize_address(**kwargs).alternatives


def test_each_alternative_has_changes_reason_and_score():
    result = alts(street1="Hauptstr. 5", city="Berlin", postal_code="10115", alternatives=5)
    assert result
    for alt in result:
        assert set(alt) == {"changes", "reason", "score"}
        assert alt["changes"] and isinstance(alt["reason"], str) and 0.0 <= alt["score"] <= 1.0
    assert {a["changes"]["country"] for a in result} >= {"USA"}
    assert [a["score"] for a in result] == sorted((a["score"] for a in result), reverse=True)


def test_country_alternatives_rank_common_countries_first_and_report_side_effects():
    result = alts(street1="Hauptstrasse 5", city="Wien", postal_code="1010", alternatives=5)
    countries = [a["changes"]["country"] for a in result if "country" in a["changes"]]
    assert "AUS" in countries and len(countries) == 5
    scores = {a["changes"]["country"]: a["score"] for a in result}
    assert scores["AUS"] == 0.4 and 0.1 in scores.values()


def test_limit_is_clamped_and_zero_means_none():
    one = alts(street1="Hauptstr. 5", city="Berlin", postal_code="10115", alternatives=1)
    assert len(one) == 1
    many = alts(street1="Hauptstr. 5", city="Berlin", postal_code="10115", alternatives=99)
    assert 1 < len(many) <= 5
    assert alts(street1="Hauptstr. 5", city="Berlin", postal_code="10115", alternatives=-1) == []
    assert alts(street1="Hauptstr. 5", city="Berlin", postal_code="10115", alternatives=0) is None


def test_no_country_alternatives_when_country_was_supplied_or_strongly_inferred():
    supplied = alts(street1="100 Main St", city="Los Angeles", state="CA", postal_code="90012", country="USA",
                    alternatives=5)
    assert supplied == []
    from_state = alts(street1="100 Main St", city="Los Angeles", state="CA", postal_code="90012", alternatives=5)
    assert from_state == []


def test_healed_city_offers_the_supplied_spelling():
    result = alts(street1="1 Main St", city="dever", state="CO", postal_code="80202", country="USA", alternatives=3)
    assert result[0] == {
        "changes": {"city": "DEVER"}, "reason": "the supplied spelling may already be correct", "score": 0.4,
    }


def test_ambiguous_city_without_state_lists_every_nearest_candidate():
    result = alts(street1="1 Main St", city="Dever", country="USA", alternatives=5)
    cities = [a["changes"]["city"] for a in result]
    assert {"DENVER", "DOVER"} <= set(cities)
    near = [a for a in result if a["changes"]["city"] in ("DENVER", "DOVER")]
    assert all(a["score"] == 0.35 for a in near)


def test_known_city_is_never_ambiguous():
    assert alts(street1="1 Main St", city="Denver", state="CO", postal_code="80202", country="USA",
                alternatives=3) == []


def test_unit_split_alternative():
    result = alts(street1="100 Main Street Suite 200", city="Austin", state="TX", postal_code="78701",
                  country="USA", alternatives=3)
    unit = next(a for a in result if "street2" in a["changes"])
    assert unit["changes"] == {"street1": "100 MAIN STREET SUITE 200", "street2": ""}
    assert unit["score"] == 0.3


def test_results_are_deterministic_and_sorted():
    kwargs = dict(street1="100 Main Street Suite 200", city="Dever", postal_code="80202", alternatives=5)
    first, second = alts(**kwargs), alts(**kwargs)
    assert first == second
    assert [a["score"] for a in first] == sorted((a["score"] for a in first), reverse=True)


def test_alternatives_never_write_audit_records():
    ledger = get_audit_ledger()
    before = len(ledger.list_records())
    standardize_address(street1="Hauptstr. 5", city="Berlin", postal_code="10115", alternatives=5)
    assert len(ledger.list_records()) <= before + 1  # at most the primary result's own record
