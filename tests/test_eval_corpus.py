"""Corpus builder: Overpass fetching (mocked), labelling, deterministic engine-free renderings."""

import io
import json
import re
import urllib.error
from pathlib import Path

import pytest

from benchmarks.eval import build_osm_corpus as bc

EVAL_DIR = Path(__file__).resolve().parent.parent / "benchmarks" / "eval"


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _payload(n=3):
    return {"elements": [
        {"type": "node", "id": i, "tags": {
            "addr:housenumber": str(i), "addr:street": "Main Street", "addr:city": "Springfield",
            "addr:postcode": "02108", "addr:state": "MA"}}
        for i in range(1, n + 1)
    ]}


def test_build_query_contains_filters_and_bbox():
    q = bc.build_query((1.0, 2.0, 3.0, 4.0), "addr:city", 50)
    assert '["addr:housenumber"]["addr:street"]["addr:postcode"]["addr:city"](1.0,2.0,3.0,4.0)' in q
    assert q.endswith("out center 50;")


def test_fetch_caches_sets_user_agent_and_backs_off(tmp_path):
    seen = []
    sleeps = []

    def opener(req, timeout):
        seen.append(req)
        if len(seen) == 1:
            raise urllib.error.URLError("boom")
        return FakeResponse(json.dumps(_payload()).encode())

    out = bc.fetch_overpass("Q1", str(tmp_path), endpoints=["https://a/x", "https://b/y"], delay=2.0,
                            sleep=sleeps.append, opener=opener)
    assert len(out["elements"]) == 3
    assert seen[0].full_url == "https://a/x" and seen[1].full_url == "https://b/y"
    assert seen[1].get_header("User-agent") == bc.USER_AGENT and "github.com" in bc.USER_AGENT
    assert sleeps == [2.0]
    # second call is served from the cache without touching the network
    again = bc.fetch_overpass("Q1", str(tmp_path), opener=lambda *a, **k: pytest.fail("network used"))
    assert again == out


def test_fetch_gives_up_after_retries_and_offline_mode(tmp_path):
    sleeps = []

    def opener(req, timeout):
        raise urllib.error.URLError("down")

    with pytest.raises(bc.OverpassError):
        bc.fetch_overpass("Q2", str(tmp_path), endpoints=["https://a/x"], retries=2, delay=1.0,
                          sleep=sleeps.append, opener=opener)
    assert sleeps == [2.0, 3.0]  # exponential backoff between rounds
    with pytest.raises(bc.OverpassError):
        bc.fetch_overpass("Q3", str(tmp_path), offline=True)


def test_element_to_labels_filters_unclean_addresses():
    cfg = bc.COUNTRIES["US"]
    good = {"tags": {"addr:housenumber": "12", "addr:street": "Elm Street", "addr:city": "Boston",
                     "addr:postcode": "02108", "addr:state": "MA"}}
    assert bc.element_to_labels(good, cfg, "addr:city") == {
        "house_number": "12", "street": "Elm Street", "city": "Boston", "state": "MA", "postcode": "02108",
        "country": "USA"}
    for bad_tags in (
        {"addr:housenumber": "12;14", "addr:street": "A", "addr:city": "B", "addr:postcode": "1"},
        {"addr:housenumber": "12", "addr:street": "A" * 80, "addr:city": "B", "addr:postcode": "1"},
        {"addr:housenumber": "12", "addr:street": "A", "addr:postcode": "1"},
    ):
        assert bc.element_to_labels({"tags": bad_tags}, cfg, "addr:city") is None
    assert bc.element_to_labels({}, cfg, "addr:city") is None
    ca = bc.COUNTRIES["CA"]
    prov = {"tags": {"addr:housenumber": "1", "addr:street": "A", "addr:city": "B", "addr:postcode": "M5V",
                     "addr:province": "ON"}}
    assert bc.element_to_labels(prov, ca, "addr:city")["state"] == "ON"


def test_parse_elements_dedups():
    payload = _payload(2)
    payload["elements"].append(dict(payload["elements"][0], id=99))  # same address, other OSM id
    recs = bc.parse_elements(payload, "US", bc.COUNTRIES["US"], "addr:city")
    assert [r["id"] for r in recs] == ["US-n1", "US-n2"]


def _record(iso2="US", state="MA", street="Main Street", hn="12"):
    return {"id": f"{iso2}-n1", "country": iso2, "labels": {
        "house_number": hn, "street": street, "city": "Boston", "state": state, "postcode": "02108",
        "country": bc.COUNTRIES[iso2]["iso3"]}}


def test_render_inputs_us_styles():
    inputs = bc.render_inputs(_record(), bc.COUNTRIES["US"], seed=1)
    assert set(inputs) == set(bc.STYLES)
    assert inputs["structured"]["fields"] == {
        "street1": "12 Main Street", "city": "Boston", "state": "MA", "postal_code": "02108", "country": "US"}
    assert inputs["structured_swapped"]["fields"]["city"] == "MA"
    assert inputs["line"]["fields"]["street1"] == "12 Main Street, Boston, MA 02108"
    assert inputs["line_nocomma"]["fields"]["street1"] == "12 Main Street Boston MA 02108"
    assert inputs["line_country_text"]["fields"] == {"street1": "12 Main Street, Boston, MA 02108, United States"}
    assert inputs["line_upper"]["fields"]["street1"].isupper()
    assert inputs["line_lower"]["fields"]["street1"].islower()
    assert inputs["line_abbrev"]["fields"]["street1"] == "12 Main St, Boston, MA 02108"
    assert "02108" not in inputs["line_no_postal"]["fields"]["street1"]
    assert inputs["line_no_postal"]["unscored"] == ["postcode"]
    assert inputs["line_swapped"]["fields"]["street1"] == "12 Main Street, MA, Boston 02108"
    assert " ".join(inputs["line_messy"]["fields"]["street1"].split()).startswith("12")


def test_render_inputs_optional_styles_are_skipped():
    rec = _record("DE", state="", street="Hauptweg")
    inputs = bc.render_inputs(rec, bc.COUNTRIES["DE"], seed=1)
    assert "structured_swapped" not in inputs and "line_swapped" not in inputs
    assert "line_abbrev" not in inputs  # nothing to abbreviate
    assert inputs["line"]["fields"]["street1"] == "Hauptweg 12, 02108 Boston"
    assert "line_abbrev" in bc.render_inputs(_record("DE", "", "Hauptstraße"), bc.COUNTRIES["DE"], 1)


def test_render_is_deterministic_and_seed_sensitive():
    a = bc.render_inputs(_record(), bc.COUNTRIES["US"], seed=7)
    assert a == bc.render_inputs(_record(), bc.COUNTRIES["US"], seed=7)
    messy = {bc.render_inputs(_record(), bc.COUNTRIES["US"], seed=s)["line_messy"]["fields"]["street1"] for s in range(12)}
    assert len(messy) > 1


def test_abbreviate_variants():
    assert bc._abbreviate("Hauptstraße 5", "de") == "Haupt" + "str. 5"
    assert bc._abbreviate("Calle Mayor 3", "es") == "C/ Mayor 3"
    assert bc._abbreviate("5 Fifth Avenue", "en") == "5 Fifth Ave"
    assert bc._abbreviate("5 Elm Street, Boston", "en") == "5 Elm St, Boston"
    assert bc._abbreviate("anything", "xx") == "anything"


def test_build_corpus_with_fake_fetcher_is_reproducible():
    calls = []

    def fetcher(query):
        calls.append(query)
        if "37.74" in query:  # simulate one failing area
            raise bc.OverpassError("nope")
        return _payload(6)

    logs = []
    c1 = bc.build_corpus(["US", "DE"], per_country=2, seed=5, cache_dir="unused", fetcher=fetcher, log=logs.append)
    c2 = bc.build_corpus(["US", "DE"], per_country=2, seed=5, cache_dir="unused", fetcher=fetcher)
    assert c1 == c2
    assert [r["country"] for r in c1].count("US") == 2 and all("inputs" in r for r in c1)
    assert any("usable candidates" in m for m in logs)

    def broken(query):
        raise bc.OverpassError("down")

    log2 = []
    assert bc.build_corpus(["US"], 2, 5, "unused", fetcher=broken, log=log2.append) == []
    assert any("skipped" in m for m in log2)


def test_write_corpus_roundtrip(tmp_path):
    corpus = bc.build_corpus(["US"], 2, 3, "unused", fetcher=lambda q: _payload(4))
    out = tmp_path / "c.json"
    bc.write_corpus(corpus, str(out), seed=3, meta={"countries": ["US"]})
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["_meta"]["records"] == 2 and data["_meta"]["seed"] == 3 and data["records"] == corpus


def test_builder_never_imports_the_engine():
    src = (EVAL_DIR / "build_osm_corpus.py").read_text(encoding="utf-8")
    assert not re.search(r"^\s*(from|import)\s+address_standardizer", src, re.M)


def test_committed_sample_is_well_formed_and_licensed():
    data = json.loads((EVAL_DIR / "osm_sample.json").read_text(encoding="utf-8"))
    recs = data["records"]
    assert 100 <= len(recs) <= 320
    countries = {r["country"] for r in recs}
    assert len(countries) >= 12
    assert {r["script"] for r in recs} - {"Latin"}, "sample must include non-Latin scripts"
    assert len({r["id"] for r in recs}) == len(recs)
    for r in recs:
        assert r["labels"]["street"] and r["labels"]["house_number"] and r["labels"]["postcode"]
        assert r["inputs"]["structured"]["fields"]["street1"]
    assert "ODbL" in data["_meta"]["license"]
    license_text = (EVAL_DIR / "DATA_LICENSE.md").read_text(encoding="utf-8")
    assert "OpenStreetMap contributors" in license_text and "NOT human-reviewed" in license_text


def _overlap(a, b):
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


def test_holdout_bboxes_are_disjoint_from_development_bboxes():
    holdout = {k: c["holdout_bboxes"] for k, c in bc.COUNTRIES.items() if c.get("holdout_bboxes")}
    assert len(holdout) >= 35
    for iso2, boxes in holdout.items():
        for h in boxes:
            for dev in bc.COUNTRIES[iso2]["bboxes"]:
                assert not _overlap(h, dev), f"{iso2} holdout box {h} overlaps development box {dev}"


def test_build_corpus_holdout_flag_selects_holdout_bboxes_only():
    seen = []

    def fetcher(query):
        seen.append(query)
        return _payload(5)

    cfg = bc.COUNTRIES["US"]
    bc.build_corpus(["US"], 2, 5, "unused", fetcher=fetcher)
    dev_queries, seen[:] = list(seen), []
    bc.build_corpus(["US"], 2, 5, "unused", fetcher=fetcher, holdout=True)
    assert len(dev_queries) == len(cfg["bboxes"]) and len(seen) == len(cfg["holdout_bboxes"])
    assert not set(dev_queries) & set(seen)
    # a holdout-only country has nothing to fetch in the default (development) mode
    assert bc.build_corpus(["MX"], 2, 5, "unused", fetcher=fetcher) == []


def test_holdout_v2_bboxes_are_disjoint_from_development_and_v1_and_each_other():
    v2 = {k: c["holdout_v2_bboxes"] for k, c in bc.COUNTRIES.items() if c.get("holdout_v2_bboxes")}
    assert len(v2) >= 40
    for iso2, boxes in v2.items():
        earlier = bc.COUNTRIES[iso2].get("bboxes", []) + bc.COUNTRIES[iso2].get("holdout_bboxes", [])
        for i, box in enumerate(boxes):
            for other in earlier + boxes[:i]:
                assert not _overlap(box, other), f"{iso2} v2 box {box} overlaps {other}"


def test_build_corpus_holdout_v2_flag_selects_v2_bboxes_only():
    seen = []

    def fetcher(query):
        seen.append(query)
        return _payload(5)

    cfg = bc.COUNTRIES["US"]
    bc.build_corpus(["US"], 2, 5, "unused", fetcher=fetcher, holdout_v2=True)
    assert len(seen) == len(cfg["holdout_v2_bboxes"])
    v1_queries = [bc.build_query(b, "addr:city", 150) for b in cfg["holdout_bboxes"] + cfg["bboxes"]]
    assert not set(seen) & set(v1_queries)
    # a country with no v1/dev boxes (ID) has nothing to fetch outside --holdout-v2
    seen[:] = []
    assert bc.build_corpus(["ID"], 2, 5, "unused", fetcher=fetcher) == []
    assert bc.build_corpus(["ID"], 2, 5, "unused", fetcher=fetcher, holdout=True) == [] and not seen


def test_committed_holdout_v2_is_well_formed_licensed_and_disjoint_from_earlier_sets():
    data = json.loads((EVAL_DIR / "osm_holdout_v2.json").read_text(encoding="utf-8"))
    recs = data["records"]
    assert data["_meta"].get("holdout_v2") is True and data["_meta"]["seed"] == bc.HOLDOUT_V2_SEED
    assert len(recs) >= 1100
    per_country = {}
    for r in recs:
        per_country[r["country"]] = per_country.get(r["country"], 0) + 1
    assert len(per_country) >= 40
    assert sum(1 for n in per_country.values() if n >= 30) >= 35
    assert {r["script"] for r in recs} - {"Latin"}
    assert len({r["id"] for r in recs}) == len(recs)
    for r in recs:
        assert r["labels"]["street"] and r["labels"]["house_number"] and r["labels"]["postcode"]
        assert r["inputs"]["structured"]["fields"]["street1"]
        assert r["source"].startswith("osm:")
    for name in ("osm_sample.json", "osm_holdout.json"):
        other = json.loads((EVAL_DIR / name).read_text(encoding="utf-8"))
        assert not {r["source"] for r in recs} & {r["source"] for r in other["records"]}, name
        assert not {r["id"] for r in recs} & {r["id"] for r in other["records"]}, name
    assert "ODbL" in data["_meta"]["license"]
    license_text = (EVAL_DIR / "DATA_LICENSE.md").read_text(encoding="utf-8")
    assert "osm_holdout_v2.json" in license_text and "NOT human-reviewed" in license_text


def test_committed_holdout_is_well_formed_licensed_and_disjoint_from_sample():
    data = json.loads((EVAL_DIR / "osm_holdout.json").read_text(encoding="utf-8"))
    sample = json.loads((EVAL_DIR / "osm_sample.json").read_text(encoding="utf-8"))
    recs = data["records"]
    assert data["_meta"].get("holdout") is True and data["_meta"]["seed"] != sample["_meta"]["seed"]
    assert len(recs) >= 400
    per_country = {}
    for r in recs:
        per_country[r["country"]] = per_country.get(r["country"], 0) + 1
    assert len(per_country) >= 20
    assert sum(1 for n in per_country.values() if n >= 25) >= 15
    assert {r["script"] for r in recs} - {"Latin"}, "holdout must include non-Latin scripts"
    assert len({r["id"] for r in recs}) == len(recs)
    for r in recs:
        assert r["labels"]["street"] and r["labels"]["house_number"] and r["labels"]["postcode"]
        assert r["inputs"]["structured"]["fields"]["street1"]
        assert r["source"].startswith("osm:")
    # no OSM object may appear in both the development sample and the held-out set
    assert not {r["source"] for r in recs} & {r["source"] for r in sample["records"]}
    assert "ODbL" in data["_meta"]["license"]
    license_text = (EVAL_DIR / "DATA_LICENSE.md").read_text(encoding="utf-8")
    assert "osm_holdout.json" in license_text and "NOT human-reviewed" in license_text
