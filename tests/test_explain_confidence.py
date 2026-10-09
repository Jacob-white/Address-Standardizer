"""Per-field confidence: derived from observable evidence, bounded, honest about being heuristic."""

from types import SimpleNamespace

import pytest

from address_standardizer import standardize_address
from address_standardizer.calibration import Calibrator, fit_isotonic
from address_standardizer.confidence import FIELD_CONFIDENCE_FIELDS, compute_field_confidence

US_KW = dict(street1="100 Main St", city="Austin", state="TX", postal_code="78701", country="USA")


def conf(**kwargs):
    kwargs.setdefault("finalize", False)
    return standardize_address(explain=True, **kwargs).field_confidence


def std(**overrides):
    base = dict(street1="100 MAIN ST", street2="", city="AUSTIN", state="TX", postal_code="78701", country="USA",
                is_us=True, is_private_residence=False, failure_reason_codes=[])
    base.update(overrides)
    return SimpleNamespace(**base)


def test_keys_and_bounds():
    result = conf(**US_KW)
    assert tuple(result) == FIELD_CONFIDENCE_FIELDS
    assert all(0.0 <= v <= 1.0 for v in result.values())


def test_clean_supplied_us_address_is_confident():
    result = conf(**US_KW)
    assert result["street1"] >= 0.95 and result["city"] >= 0.9 and result["state"] >= 0.97
    assert result["postal_code"] >= 0.95 and result["country"] == 0.99 and result["street2"] == 1.0


def test_inferred_and_healed_fields_are_less_certain_than_supplied_ones():
    supplied = conf(**US_KW)
    healed = conf(street1="100 Main St", city="Austn", state="TX", postal_code="78701", country="USA")
    assert healed["city"] < supplied["city"]
    from_zip = conf(street1="100 Main St", city="Austin", postal_code="78701", country="USA")
    assert from_zip["state"] < supplied["state"]
    no_country = conf(street1="100 Main St", city="Austin", state="TX", postal_code="78701")
    assert no_country["country"] < supplied["country"]


def test_zip_state_agreement_and_mismatch():
    agree = conf(**US_KW)
    mismatch = conf(street1="100 Main St", city="Los Angeles", state="NY", postal_code="90012", country="USA")
    assert mismatch["state"] == 0.35 and agree["state"] > mismatch["state"]
    corrected = conf(street1="100 Main St", city="Los Angeles", state="NY", postal_code="90012", country="USA",
                     correct_state_from_zip=True)
    assert corrected["state"] == 0.82


def test_finalized_failure_codes_lower_street_confidence():
    plain = conf(**{**US_KW, "street1": "Main St"}, finalize=True)
    assert plain["street1"] < 0.7  # ERR_MISSING_HOUSE_NUM
    campus = conf(street1="Stanford University", city="Stanford", state="CA", postal_code="94305", country="USA",
                  finalize=True)
    assert campus["street1"] < 0.9


def test_parse_path_sets_the_street_baseline():
    fast = conf(**US_KW)["street1"]
    grammar = conf(street1="Hauptstrasse 5", city="Berlin", postal_code="10115", country="DEU")["street1"]
    assert fast > grammar


def test_missing_values_score_zero_and_not_applicable_scores_one():
    result = conf(street1="100 Main St", country="USA")
    assert result["city"] == 0.0 and result["state"] == 0.0 and result["postal_code"] == 0.0
    german = conf(street1="Hauptstrasse 5", city="Berlin", postal_code="10115", country="DEU")
    assert german["state"] == 1.0 and german["street2"] == 1.0
    empty = conf(country="USA")
    assert empty["street1"] == 0.0


def test_invalid_postal_format():
    result = conf(street1="10 Downing Street", city="London", postal_code="123", country="GBR")
    assert result["postal_code"] == 0.3


def test_private_residence_and_secondary_unit_rules():
    private = conf(street1="Private Residence", city="Austin", state="TX", postal_code="78701", country="USA")
    assert private["street1"] == 0.3
    unit = conf(street1="100 Main St", street2="Suite 5", city="Austin", state="TX", postal_code="78701",
                country="USA")
    assert unit["street2"] == 0.97
    split = conf(street1="100 Main St Suite 5", city="Austin", state="TX", postal_code="78701", country="USA")
    assert split["street2"] == 0.85
    words = conf(street1="100 Main St", street2="Suite Five", city="Austin", state="TX", postal_code="78701",
                 country="USA")
    assert words["street2"] == 0.95


class TestEvidenceTable:
    """The scoring function on hand-built evidence, so every rule is pinned independently of the parsers."""

    def test_defaults_without_evidence(self):
        out = compute_field_confidence(std())
        assert out["street1"] == 0.9 and out["country"] == 0.99

    def test_street_penalties(self):
        ev = {"parse_path": "us_parser", "distances": {"street1": 2},
              "rules": {"street1": ["typo_heal_street", "secondary_promoted_to_street", "token_rewritten"]}}
        assert compute_field_confidence(std(), ev)["street1"] == pytest.approx(0.95 - 0.16 - 0.10 - 0.04)
        codes = ["ERR_MISSING_HOUSE_NUM", "ERR_UNRESOLVED_SUFFIX", "WARN_LANDMARK_CAMPUS_PREMISE"]
        out = compute_field_confidence(std(failure_reason_codes=codes), {"parse_path": "fast_path"})
        assert out["street1"] == 0.29
        assert compute_field_confidence(std(), {"parse_path": "universal_grammar"})["street1"] == 0.8

    def test_street2(self):
        assert compute_field_confidence(std(failure_reason_codes=["WARN_MISSING_SECONDARY_UNIT"]))["street2"] == 0.5
        ev = {"supplied": {"street2": True}, "rules": {"street2": ["street1_moved_to_street2"]}}
        assert compute_field_confidence(std(street2="STE 5"), ev)["street2"] == 0.82

    def test_city(self):
        cases = [
            ({"typo_heal_city": 0.0}, 2, 0.7), ({"city_inferred_from_text": 0}, 0, 0.7),
            ({"city_canonicalized": 0}, 0, 0.85),
        ]
        for rules, dist, expected in cases:
            ev = {"rules": {"city": list(rules)}, "distances": {"city": dist}}
            assert compute_field_confidence(std(), ev)["city"] == expected
        assert compute_field_confidence(std(city=""))["city"] == 0.0
        assert compute_field_confidence(std(), {"reference_status": "confirmed"})["city"] == 0.99
        assert compute_field_confidence(std(), {"reference_status": "place_mismatch"})["city"] == 0.57

    def test_state(self):
        def st(rule=None, **ev):
            evidence = dict(ev)
            if rule:
                evidence["rules"] = {"state": [rule]}
            return compute_field_confidence(std(), evidence)["state"]

        assert st("state_corrected_from_zip") == 0.8 and st("state_from_zip") == 0.85
        assert st("state_inferred_from_text") == 0.8 and st() == 0.97
        assert st(zip_state="agree") == 0.99 and st(zip_state="mismatch") == 0.35
        assert st(reference_status="state_mismatch") == 0.3
        assert compute_field_confidence(std(state="ZZ"))["state"] == 0.2
        assert compute_field_confidence(std(state="", is_us=False))["state"] == 1.0
        assert compute_field_confidence(std(failure_reason_codes=["ERR_ZIP_STATE_MISMATCH"]))["state"] == 0.35

    def test_postal(self):
        def pc(rule=None, **ev):
            evidence = dict(ev)
            if rule:
                evidence["rules"] = {"postal_code": [rule]}
            return compute_field_confidence(std(), evidence)["postal_code"]

        assert pc("postal_transposition_healed") == 0.7 and pc("postal_extracted_from_text") == 0.85
        assert pc() == 0.97 and pc(postal_valid=False) == 0.3
        assert pc(reference_status="postal_unknown") == 0.3
        assert pc(reference_status="confirmed") == 1.0 and pc(reference_status="place_mismatch") == 1.0
        assert compute_field_confidence(std(postal_code=""))["postal_code"] == 0.0

    def test_country(self):
        def cc(rule):
            return compute_field_confidence(std(), {"rules": {"country": [rule]}})["country"]

        assert cc("country_inferred_from_script") == 0.8 and cc("country_inferred_from_state") == 0.9
        assert cc("country_inferred_from_postal") == 0.75 and cc("country_inferred_from_text") == 0.7
        assert cc("country_defaulted_us") == 0.6 and cc("country_normalized") == 0.99
        assert compute_field_confidence(std(country=""))["country"] == 0.0
        assert compute_field_confidence(std(country="United States"))["country"] == 0.5


class TestCalibrator:
    def test_default_is_uncalibrated(self):
        assert conf(**US_KW) == standardize_address(explain=True, finalize=False, calibrator=None, **US_KW).field_confidence

    def test_calibrator_maps_every_field_and_stays_in_range(self):
        calibrator = Calibrator([0.0, 1.0], [0.0, 0.5])
        raw = conf(**US_KW)
        mapped = standardize_address(explain=True, finalize=False, calibrator=calibrator, **US_KW).field_confidence
        assert mapped == {k: round(v * 0.5, 4) for k, v in raw.items()}

    def test_fitted_calibrator_is_applied(self):
        calibrator = fit_isotonic([(0.2, False), (0.4, False), (0.9, True), (1.0, True)])
        out = compute_field_confidence(std(), {"parse_path": "fast_path"}, calibrator)
        assert all(0.0 <= v <= 1.0 for v in out.values())


def test_composite_score_and_routing_are_unchanged_by_explain():
    plain = standardize_address(use_cache=False, **US_KW)
    explained = standardize_address(explain=True, alternatives=3, **US_KW)
    assert (plain.confidence_score, plain.routing_tier) == (explained.confidence_score, explained.routing_tier)


@pytest.mark.parametrize("field", FIELD_CONFIDENCE_FIELDS)
def test_every_field_is_reported(field):
    assert field in conf(**US_KW)
