"""Evaluation runner: comparison rules, metrics, baseline logic, and the committed-sample baseline gate."""

import json
from pathlib import Path

import pytest

from benchmarks.eval import run_eval as ev

EVAL_DIR = Path(__file__).resolve().parent.parent / "benchmarks" / "eval"


def test_wilson_interval():
    assert ev.wilson(0, 0) == (0.0, 1.0)
    lo, hi = ev.wilson(50, 100)
    assert lo == pytest.approx(0.4038, abs=1e-3) and hi == pytest.approx(0.5962, abs=1e-3)
    lo, hi = ev.wilson(10, 10)
    assert hi == 1.0 and lo == pytest.approx(0.7225, abs=1e-3)
    assert ev.wilson(0, 10)[0] == 0.0


def test_text_normalisation_rules():
    assert ev.tokens("Hauptstraße 5-A") == ["hauptstrasse", "5", "a"]
    assert ev.tokens("Café Müller") == ["cafe", "muller"]
    assert ev.street_tokens("5 HAUPTSTR.", "5") == ev.street_tokens("Hauptstraße")
    assert ev.street_tokens("12 N MAIN ST", "12") == ev.street_tokens("North Main Street")
    assert ev.street_tokens("350 5TH AVE", "350") == ev.street_tokens("Fifth Avenue")
    assert ev.street_tokens("Av. de la Paz") == ev.street_tokens("Avenida de la Paz")
    assert ev.street_tokens("ул. Тверская") == ev.street_tokens("улица Тверская")
    assert ev.canon_state("Massachusetts") == ev.canon_state("MA") == "ma"
    assert ev.canon_state("Bayern") == "bayern"
    assert ev.canon_postcode("sw1a 1aa") == "sw1a1aa"


def test_house_number_matching_is_strict_but_format_tolerant():
    assert ev.house_number_found("12 MAIN ST", "12")
    assert not ev.house_number_found("123 MAIN ST", "12")
    assert ev.house_number_found("12A MAIN ST", "12A") and ev.house_number_found("12 A MAIN ST", "12A")
    assert ev.house_number_found("MAIN ST 12 - 14", "12-14") and ev.house_number_found("X 1 2 3", "123")
    assert not ev.house_number_found("MAIN ST", "")
    assert ev.has_house_number_candidate("MAIN 4") and not ev.has_house_number_candidate("MAIN ST")


def test_postcode_rules():
    assert ev.postcodes_match("02108", "02108-1234") and ev.postcodes_match("02108-1234", "02108")
    assert ev.postcodes_match("SW1A 1AA", "sw1a1aa")
    assert not ev.postcodes_match("02108", "02109")
    assert not ev.postcodes_match("1234", "12345")  # prefix rule needs >= 5 digits
    assert not ev.postcodes_match("EC1A", "EC1A1BB")
    assert not ev.postcodes_match("", "02108")


LABELS = {"house_number": "12", "street": "Main Street", "city": "Boston", "state": "Massachusetts",
          "postcode": "02108", "country": "USA"}
GOOD = {"street1": "12 MAIN ST", "city": "BOSTON", "state": "MA", "postal_code": "02108", "country": "USA"}


def test_judge_fields_correct_wrong_missing_and_unscored():
    v = ev.judge_fields(LABELS, GOOD, [])
    assert {f: o for f, (o, _) in v.items()} == {f: "correct" for f in ev.FIELDS}

    bad = {"street1": "13 ELM ST", "city": "CAMBRIDGE", "state": "NY", "postal_code": "02139", "country": "CAN"}
    assert {f: o for f, (o, _) in ev.judge_fields(LABELS, bad, []).items()} == {f: "wrong" for f in ev.FIELDS}

    empty = {"street1": "", "city": "", "state": None, "postal_code": None, "country": ""}
    assert {f: o for f, (o, _) in ev.judge_fields(LABELS, empty, []).items()} == {f: "missing" for f in ev.FIELDS}

    nonum = dict(GOOD, street1="MAIN ST")
    assert ev.judge_fields(LABELS, nonum, [])["house_number"][0] == "missing"

    v = ev.judge_fields(dict(LABELS, state=""), GOOD, ["postcode"])
    assert "state" not in v and "postcode" not in v and "street" in v


def _corpus():
    def rec(rid, country, street1):
        return {"id": rid, "country": country, "script": "Latin", "labels": LABELS,
                "inputs": {"line": {"fields": {"street1": street1, "country": "US"}},
                           "line_no_postal": {"fields": {"street1": street1}, "unscored": ["postcode"]}}}
    return {"_meta": {"seed": 1}, "records": [rec("US-1", "US", "ok"), rec("US-2", "US", "bad"),
                                               rec("CA-1", "CA", "boom")]}


def _engine(fields):
    if fields["street1"] == "boom":
        raise RuntimeError("engine exploded")
    if fields["street1"] == "ok":
        return dict(GOOD, confidence=0.99, tier="AUTO_PASS")
    return {"street1": "99 OTHER RD", "city": "BOSTON", "state": "MA", "postal_code": "", "country": "USA",
            "confidence": 0.5, "tier": "X"}


def test_evaluate_aggregate_and_report():
    corpus = _corpus()
    rows = ev.evaluate(corpus, _engine)
    assert len(rows) == 6
    boom = [r for r in rows if r["id"] == "CA-1"][0]
    assert boom["error"].startswith("RuntimeError") and not boom["exact"] and boom["confidence"] == 0.0
    assert all(set(r["outcomes"]) == set(ev.FIELDS) - ({"postcode"} if r["style"] == "line_no_postal" else set())
               for r in rows if r["id"] == "US-1")

    report = ev.build_report(corpus, rows)
    m = report["metrics"]
    assert m["exact_overall"]["n"] == 6 and m["exact_overall"]["exact"] == 2
    assert m["exact_by_country"]["US"]["exact"] == 2 and m["exact_by_country"]["CA"]["exact"] == 0
    city = m["by_country"]["US"]["city"]
    assert city["n"] == 4 and city["correct"] == 4 and city["precision"] == 1.0
    pc = m["overall_by_field"]["postcode"]
    assert pc["n"] == 3 and pc["correct"] == 1 and pc["missing"] == 2 and pc["precision"] == 1.0
    assert m["by_style"]["line_no_postal"]["street"]["n"] == 3
    assert report["n_renderings"] == 6 and len(report["rows"]) == 6

    worst = report["worst_failures"]
    assert worst[0]["id"] == "CA-1" and "error" in worst[0]
    assert report["calibration"]["n"] == 6

    md = ev.to_markdown(report)
    assert "All-fields exact match" in md and "## Worst failures" in md and "ECE =" in md
    json.dumps(report)  # serialisable


def test_precision_none_when_nothing_predicted():
    rows = ev.evaluate({"records": [{"id": "X-1", "country": "XX", "labels": {"street": "A", "house_number": "1"},
                                     "inputs": {"s": {"fields": {"street1": "q"}}}}]},
                       lambda f: {"street1": "", "confidence": 0.1})
    agg = ev.aggregate(rows)
    assert agg["overall_by_field"]["street"]["precision"] is None
    assert ev._pct(None) == "-"
    assert ev.calibration_summary([]) is None


def test_markdown_handles_missing_fields_and_no_calibration():
    rows = ev.evaluate(_corpus(), _engine)
    report = ev.build_report(_corpus(), rows)
    report["calibration"] = None
    del report["metrics"]["by_country"]["US"]["state"]
    md = ev.to_markdown(report)
    assert "Raw confidence score" not in md and "| - (" not in md and " - |" in md


def test_baseline_roundtrip_and_regression_detection():
    corpus = _corpus()
    report = ev.build_report(corpus, ev.evaluate(corpus, _engine))
    base = ev.baseline_from_report(report, tolerance=0.02)
    assert ev.check_baseline(report, base) == []

    worse = ev.build_report(corpus, ev.evaluate(corpus, lambda f: {"street1": "", "confidence": 0.0}))
    problems = ev.check_baseline(worse, base)
    assert any(p.startswith("US/city") for p in problems)
    assert any("exact" in p for p in problems)
    # a generous tolerance accepts the drop on accuracies but exact-match still reported with tol 1.0 -> none
    assert ev.check_baseline(worse, base, tolerance=1.0) == []

    missing = json.loads(json.dumps(base))
    missing["accuracy"]["ZZ"] = {"city": 0.9}
    missing["exact"]["ZZ"] = 0.9
    probs = ev.check_baseline(report, missing)
    assert any("ZZ/city: missing" in p for p in probs) and any("ZZ/exact" in p for p in probs)

    raised = json.loads(json.dumps(base))
    raised["exact_overall"] = 1.0
    assert any(p.startswith("overall exact") for p in ev.check_baseline(report, raised))


def test_load_corpus_reads_utf8(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"records": [{"id": "x", "n": "Straße"}]}, ensure_ascii=False), encoding="utf-8")
    assert ev.load_corpus(str(p))["records"][0]["n"] == "Straße"


def test_default_engine_runs_real_standardizer():
    out = ev.default_engine({"street1": "100 Wall St", "city": "New York", "state": "NY", "postal_code": "10005",
                             "country": "US"})
    assert out["street1"].startswith("100 WALL") and out["country"] == "USA" and 0 < out["confidence"] <= 1


def test_committed_sample_meets_baseline():
    """Regression gate on independent OSM-derived data. The baseline records CURRENT results (not a target)."""
    corpus = ev.load_corpus(str(EVAL_DIR / "osm_sample.json"))
    report = ev.build_report(corpus, ev.evaluate(corpus))
    baseline = json.loads((EVAL_DIR / "baseline.json").read_text(encoding="utf-8"))
    assert report["n_records"] == baseline["n_records"]
    problems = ev.check_baseline(report, baseline)
    assert not problems, "accuracy on the OSM sample regressed:\n" + "\n".join(problems)


def test_turkish_dotted_dotless_i_folds_to_one_letter():
    assert ev.tokens("Kızılırmak") == ev.tokens("KIZILIRMAK") == ["kizilirmak"]
    assert ev.tokens("İzmir") == ev.tokens("IZMIR") == ev.tokens("İZMIR") == ["izmir"]
    # genuinely different streets still differ
    assert ev.tokens("Kızılırmak") != ev.tokens("Kizilirmak Mah")
    labels = {"street": "Şair Eşref Bulvarı", "house_number": "63", "country": "TUR"}
    ok = ev.judge_fields(labels, {"street1": "ŞAIR EŞREF BULVARI 63"}, [])
    assert ok["street"][0] == "correct"
    other = ev.judge_fields(labels, {"street1": "ŞAIR EŞREF CADDESI 63"}, [])
    assert other["street"][0] == "wrong"


def test_canadian_french_directionals_and_types():
    can = {"street": "Avenue Viger Ouest", "house_number": "9", "country": "CAN"}
    assert ev.judge_fields(can, {"street1": "9 AV VIGER O"}, [])["street"][0] == "correct"
    assert ev.judge_fields(can, {"street1": "9 AV VIGER OUEST"}, [])["street"][0] == "correct"
    # a different direction, a different street or a missing directional still mismatch
    assert ev.judge_fields(can, {"street1": "9 AV VIGER E"}, [])["street"][0] == "wrong"
    assert ev.judge_fields(can, {"street1": "9 AV VIGER"}, [])["street"][0] == "wrong"
    assert ev.judge_fields(can, {"street1": "9 AV VIGNEAU O"}, [])["street"][0] == "wrong"
    boul = {"street": "Boulevard Saint-Laurent Est", "house_number": "1", "country": "CAN"}
    assert ev.judge_fields(boul, {"street1": "1 BOUL SAINT-LAURENT E"}, [])["street"][0] == "correct"
    # English labels in Canada keep matching through the same class
    eng = {"street": "King Street East", "house_number": "5", "country": "CAN"}
    assert ev.judge_fields(eng, {"street1": "5 KING ST E"}, [])["street"][0] == "correct"
    # outside Canada "O"/"E" are not equated with Ouest/East
    fr = {"street": "Rue Haute Ouest", "house_number": "2", "country": "FRA"}
    assert ev.judge_fields(fr, {"street1": "2 RUE HAUTE O"}, [])["street"][0] == "wrong"
    assert ev.street_tokens("Rue X Ouest", french=True) == ev.street_tokens("Rue X O", french=True)
    assert ev.street_tokens("Rue X Ouest") != ev.street_tokens("Rue X O")
