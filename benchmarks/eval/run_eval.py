"""
Independent accuracy evaluation runner.
=======================================
Runs ``standardize_address`` on every rendering of every record in an OSM-derived corpus (see
build_osm_corpus.py), compares the output with the OSM ground-truth labels using SAFE comparison rules, and
reports accuracy / precision / recall per field, per country and per input style with Wilson confidence
intervals, an all-fields exact-match rate, the worst failures and the raw confidence-score calibration.

    PYTHONPATH=. python benchmarks/eval/run_eval.py --corpus benchmarks/eval/osm_sample.json \
        --out-json /tmp/eval.json --out-md /tmp/eval.md [--baseline benchmarks/eval/baseline.json]

Metric definitions (per scored field):
  * labelled   = renderings whose ground truth has a value for the field and where the input kept it
  * correct    = engine output matches the label under the normalisation rules below
  * wrong      = engine produced a value that does not match;  missing = engine produced nothing
  * accuracy   = recall = correct / labelled;   precision = correct / (correct + wrong)
No tolerance is applied beyond the documented normalisation: case, accents, punctuation, street-type and
directional abbreviations, ordinal words, leading zeros are NOT ignored for house numbers, ZIP+4 truncation.
"""

import argparse
import json
import math
import os
import sys
import unicodedata
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from address_standardizer.calibration import (  # noqa: E402
    brier_score,
    expected_calibration_error,
    reliability_bins,
)

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ("house_number", "street", "city", "state", "postcode", "country")

# --------------------------------------------------------------------------- normalisation (engine-free)

_TYPE_CANON = {
    # English
    "st": "street", "str": "street", "ave": "avenue", "av": "avenue", "avda": "avenue", "avenida": "avenue",
    "rd": "road", "blvd": "boulevard", "bd": "boulevard", "dr": "drive", "ln": "lane", "ct": "court",
    "pl": "place", "ter": "terrace", "hwy": "highway", "pkwy": "parkway", "cir": "circle", "sq": "square",
    "cswy": "causeway", "aly": "alley", "xing": "crossing", "pky": "parkway", "expy": "expressway",
    "fwy": "freeway", "trl": "trail", "trce": "trace", "hts": "heights", "jct": "junction", "plz": "plaza",
    "ctr": "center", "cres": "crescent", "gdns": "gardens", "gdn": "garden", "grn": "green", "grv": "grove",
    "rdg": "ridge", "rte": "route", "brg": "bridge", "pk": "park", "mt": "mount", "mtn": "mountain",
    "n": "north", "s": "south", "e": "east", "w": "west", "ne": "northeast", "nw": "northwest",
    "se": "southeast", "sw": "southwest",
    # Romance / Slavic / other common abbreviations
    "c": "calle", "pza": "plaza", "pz": "plaza", "piazza": "plaza", "r": "rua", "tv": "travessa", "pc": "praca",
    "ul": "ulica", "al": "aleja",
    "ул": "улица", "пр": "проспект", "просп": "проспект", "пер": "переулок", "бул": "бульвар", "вул": "вулиця",
    "пров": "провулок",
}
_ORDINALS = {
    "first": "1st", "second": "2nd", "third": "3rd", "fourth": "4th", "fifth": "5th", "sixth": "6th",
    "seventh": "7th", "eighth": "8th", "ninth": "9th", "tenth": "10th", "eleventh": "11th", "twelfth": "12th",
}
_STATE_CODES = {
    "alabama": "al", "alaska": "ak", "arizona": "az", "arkansas": "ar", "california": "ca", "colorado": "co",
    "connecticut": "ct", "delaware": "de", "district of columbia": "dc", "florida": "fl", "georgia": "ga",
    "hawaii": "hi", "idaho": "id", "illinois": "il", "indiana": "in", "iowa": "ia", "kansas": "ks",
    "kentucky": "ky", "louisiana": "la", "maine": "me", "maryland": "md", "massachusetts": "ma",
    "michigan": "mi", "minnesota": "mn", "mississippi": "ms", "missouri": "mo", "montana": "mt",
    "nebraska": "ne", "nevada": "nv", "new hampshire": "nh", "new jersey": "nj", "new mexico": "nm",
    "new york": "ny", "north carolina": "nc", "north dakota": "nd", "ohio": "oh", "oklahoma": "ok",
    "oregon": "or", "pennsylvania": "pa", "rhode island": "ri", "south carolina": "sc",
    "south dakota": "sd", "tennessee": "tn", "texas": "tx", "utah": "ut", "vermont": "vt", "virginia": "va",
    "washington": "wa", "west virginia": "wv", "wisconsin": "wi", "wyoming": "wy",
    # Canada
    "ontario": "on", "quebec": "qc", "british columbia": "bc", "alberta": "ab", "manitoba": "mb",
    "saskatchewan": "sk", "nova scotia": "ns", "new brunswick": "nb", "newfoundland and labrador": "nl",
    "prince edward island": "pe",
    # Australia
    "new south wales": "nsw", "victoria": "vic", "queensland": "qld", "western australia": "wa",
    "south australia": "sa", "tasmania": "tas", "australian capital territory": "act",
    "northern territory": "nt",
}


def _fold(text: Any) -> str:
    """Casefold, strip accents/combining marks, turn every non-alphanumeric character into a space."""
    s = unicodedata.normalize("NFKC", str(text or "")).casefold().replace("ß", "ss")
    s = "".join(ch for ch in unicodedata.normalize("NFKD", s) if unicodedata.category(ch) != "Mn")
    return "".join(ch if unicodedata.category(ch)[0] in "LN" else " " for ch in s)


def tokens(text: Any) -> List[str]:
    return _fold(text).split()


def _canon_token(tok: str) -> str:
    tok = _ORDINALS.get(tok, tok)
    tok = _TYPE_CANON.get(tok, tok)
    # German/Dutch compound suffix: "hauptstr" / "hauptstrasse" -> "hauptstrasse"
    if len(tok) > 3 and tok.endswith("str"):
        return tok + "asse"
    return tok


def street_tokens(text: Any, house_number: str = "") -> List[str]:
    """Street tokens with the house number removed and street types/directionals canonicalised."""
    hn = "".join(tokens(house_number))
    toks = tokens(text)
    if hn:
        # remove the first run of 1-4 consecutive tokens whose concatenation is the house number ("74-76" -> 74, 76)
        for i in range(len(toks)):
            if any("".join(toks[i:i + k]) == hn for k in range(1, 5)):
                k = next(k for k in range(1, 5) if "".join(toks[i:i + k]) == hn)
                toks = toks[:i] + toks[i + k:]
                break
    return [_canon_token(t) for t in toks]


def house_number_found(street1: Any, label_hn: str) -> bool:
    """True if the label house number appears as a whole token (or adjacent token pair) in street1."""
    want = "".join(tokens(label_hn))
    if not want:
        return False
    toks = tokens(street1)
    if want in toks:
        return True
    return any(a + b == want for a, b in zip(toks, toks[1:])) or any(
        a + b + c == want for a, b, c in zip(toks, toks[1:], toks[2:])
    )


def has_house_number_candidate(street1: Any) -> bool:
    return any(ch.isdigit() for ch in str(street1 or ""))


def canon_state(text: Any) -> str:
    folded = " ".join(tokens(text))
    return _STATE_CODES.get(folded, folded)


def canon_postcode(text: Any) -> str:
    return "".join(tokens(text))


def postcodes_match(label: str, pred: str) -> bool:
    a, b = canon_postcode(label), canon_postcode(pred)
    if not a or not b:
        return False
    if a == b:
        return True
    # US ZIP+4 vs ZIP5 (both purely numeric, shorter one at least 5 digits)
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    return short.isdigit() and long_.isdigit() and len(short) >= 5 and long_.startswith(short)


# --------------------------------------------------------------------------- comparison


def wilson(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion; (0, 1) when n == 0."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def judge_fields(labels: Dict[str, str], pred: Dict[str, Any], unscored: List[str]) -> Dict[str, Tuple[str, Any]]:
    """Return {field: (outcome, predicted_repr)} for scored fields. outcome in correct/wrong/missing."""
    out: Dict[str, Tuple[str, Any]] = {}
    street1 = pred.get("street1") or ""
    for field in FIELDS:
        label = labels.get(field) or ""
        if not label or field in unscored:
            continue
        if field == "house_number":
            if house_number_found(street1, label):
                out[field] = ("correct", label)
            else:
                out[field] = ("wrong" if has_house_number_candidate(street1) else "missing", street1)
        elif field == "street":
            got = street_tokens(street1, labels.get("house_number", ""))
            want = street_tokens(label)
            if not got:
                out[field] = ("missing", street1)
            else:
                out[field] = ("correct" if got == want else "wrong", street1)
        elif field == "city":
            got_c = [_canon_token(t) for t in tokens(pred.get("city"))]
            want_c = [_canon_token(t) for t in tokens(label)]
            out[field] = ("missing" if not got_c else ("correct" if got_c == want_c else "wrong"), pred.get("city"))
        elif field == "state":
            got_s = canon_state(pred.get("state"))
            out[field] = ("missing" if not got_s else ("correct" if got_s == canon_state(label) else "wrong"),
                          pred.get("state"))
        elif field == "postcode":
            got_p = pred.get("postal_code") or ""
            out[field] = ("missing" if not canon_postcode(got_p) else
                          ("correct" if postcodes_match(label, got_p) else "wrong"), got_p)
        else:  # country (ISO 3166-1 alpha-3)
            got_k = str(pred.get("country") or "").upper()
            out[field] = ("missing" if not got_k else ("correct" if got_k == label.upper() else "wrong"), got_k)
    return out


# --------------------------------------------------------------------------- engine adapter


def default_engine(fields: Dict[str, str]) -> Dict[str, Any]:
    """Run the real engine; returns the predicted fields plus the heuristic confidence score."""
    from address_standardizer import standardize_address
    from address_standardizer.confidence import compute_confidence_score

    res = standardize_address(
        street1=fields.get("street1"), street2=fields.get("street2"), city=fields.get("city"),
        state=fields.get("state"), postal_code=fields.get("postal_code"), country=fields.get("country"),
    )
    conf = compute_confidence_score(res, raw_input=fields)
    return {
        "street1": res.street1, "city": res.city, "state": res.state, "postal_code": res.postal_code,
        "country": res.country, "confidence": conf.composite_score, "tier": conf.routing_tier,
    }


def load_corpus(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def evaluate(corpus: Dict[str, Any], engine: Callable[[Dict[str, str]], Dict[str, Any]] = default_engine) -> List[Dict[str, Any]]:
    """One row per (record, style)."""
    rows: List[Dict[str, Any]] = []
    for rec in corpus["records"]:
        for style, entry in rec["inputs"].items():
            try:
                pred = engine(entry["fields"])
            except Exception as exc:  # an engine crash is a (counted) failure, never silently skipped
                pred = {"error": f"{type(exc).__name__}: {exc}", "confidence": 0.0}
            verdict = judge_fields(rec["labels"], pred, entry.get("unscored", []))
            rows.append({
                "id": rec["id"], "country": rec["country"], "style": style,
                "input": entry["fields"],
                "outcomes": {f: v[0] for f, v in verdict.items()},
                "predicted": {f: v[1] for f, v in verdict.items() if v[0] != "correct"},
                "exact": all(v[0] == "correct" for v in verdict.values()),
                "confidence": float(pred.get("confidence", 0.0)),
                "tier": pred.get("tier"),
                "error": pred.get("error"),
            })
    return rows


# --------------------------------------------------------------------------- aggregation


def _bucket() -> Dict[str, int]:
    return {"correct": 0, "wrong": 0, "missing": 0}


def _finish(b: Dict[str, int]) -> Dict[str, Any]:
    n = b["correct"] + b["wrong"] + b["missing"]
    predicted = b["correct"] + b["wrong"]
    lo, hi = wilson(b["correct"], n)
    return {
        "n": n, "correct": b["correct"], "wrong": b["wrong"], "missing": b["missing"],
        "accuracy": b["correct"] / n if n else None,
        "precision": b["correct"] / predicted if predicted else None,
        "recall": b["correct"] / n if n else None,
        "ci95": [round(lo, 4), round(hi, 4)],
    }


def aggregate(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_cf: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(_bucket)
    by_sf: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(_bucket)
    by_f: Dict[str, Dict[str, int]] = defaultdict(_bucket)
    exact_c: Dict[str, List[int]] = defaultdict(lambda: [0, 0])
    exact_s: Dict[str, List[int]] = defaultdict(lambda: [0, 0])
    exact_all = [0, 0]
    for r in rows:
        for f, o in r["outcomes"].items():
            by_cf[(r["country"], f)][o] += 1
            by_sf[(r["style"], f)][o] += 1
            by_f[f][o] += 1
        for tbl, key in ((exact_c, r["country"]), (exact_s, r["style"])):
            tbl[key][1] += 1
            tbl[key][0] += r["exact"]
        exact_all[1] += 1
        exact_all[0] += r["exact"]

    def ex(k: int, n: int) -> Dict[str, Any]:
        lo, hi = wilson(k, n)
        return {"n": n, "exact": k, "rate": k / n if n else None, "ci95": [round(lo, 4), round(hi, 4)]}

    def nest(src: Dict[Tuple[str, str], Dict[str, int]]) -> Dict[str, Dict[str, Any]]:
        out: Dict[str, Dict[str, Any]] = {}
        for (g, f), b in sorted(src.items()):
            out.setdefault(g, {})[f] = _finish(b)
        return out

    return {
        "overall_by_field": {f: _finish(by_f[f]) for f in FIELDS if f in by_f},
        "by_country": nest(by_cf),
        "by_style": nest(by_sf),
        "exact_overall": ex(*exact_all),
        "exact_by_country": {k: ex(*v) for k, v in sorted(exact_c.items())},
        "exact_by_style": {k: ex(*v) for k, v in sorted(exact_s.items())},
    }


def worst_failures(rows: List[Dict[str, Any]], limit: int = 15, per_group: int = 2) -> List[Dict[str, Any]]:
    """Rows with the most wrong fields; at most ``per_group`` per (country, style) so one failure mode cannot fill the list."""
    bad = [r for r in rows if not r["exact"]]
    bad.sort(key=lambda r: (-sum(o != "correct" for o in r["outcomes"].values()), r["id"], r["style"]))
    seen: Dict[Tuple[str, str], int] = defaultdict(int)
    picked: List[Dict[str, Any]] = []
    for r in bad:
        key = (r["country"], r["style"])
        if seen[key] >= per_group:
            continue
        seen[key] += 1
        picked.append(r)
        if len(picked) == limit:
            break
    return [{
        "id": r["id"], "style": r["style"], "input": r["input"],
        "failed": {f: o for f, o in r["outcomes"].items() if o != "correct"},
        "predicted": r["predicted"], "confidence": r["confidence"], "error": r["error"],
    } for r in picked]


def calibration_summary(rows: List[Dict[str, Any]], n_bins: int = 10) -> Optional[Dict[str, Any]]:
    pairs = [(r["confidence"], r["exact"]) for r in rows]
    if not pairs:
        return None
    return {
        "n": len(pairs),
        "base_rate_exact": sum(1 for _, ok in pairs if ok) / len(pairs),
        "ece": expected_calibration_error(pairs, n_bins),
        "brier": brier_score(pairs),
        "bins": [b.as_dict() for b in reliability_bins(pairs, n_bins)],
    }


def build_report(corpus: Dict[str, Any], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "corpus_meta": corpus.get("_meta", {}),
        "n_records": len(corpus["records"]),
        "n_renderings": len(rows),
        "metrics": aggregate(rows),
        "worst_failures": worst_failures(rows),
        "calibration": calibration_summary(rows),
        "rows": [{k: r[k] for k in ("id", "country", "style", "exact", "confidence", "tier")} for r in rows],
    }


# --------------------------------------------------------------------------- baseline


def baseline_from_report(report: Dict[str, Any], tolerance: float = 0.02) -> Dict[str, Any]:
    """Snapshot of (country, field) accuracies and exact-match rates, to be committed."""
    m = report["metrics"]
    return {
        "_note": "Current-engine snapshot on the OSM sample (NOT a target; do not tune the engine to it).",
        "tolerance": tolerance,
        "n_records": report["n_records"],
        "accuracy": {c: {f: v["accuracy"] for f, v in fields.items()} for c, fields in m["by_country"].items()},
        "exact": {c: v["rate"] for c, v in m["exact_by_country"].items()},
        "exact_overall": m["exact_overall"]["rate"],
    }


def check_baseline(report: Dict[str, Any], baseline: Dict[str, Any], tolerance: Optional[float] = None) -> List[str]:
    """Return a list of regressions (empty = pass). A drop larger than ``tolerance`` fails."""
    tol = baseline.get("tolerance", 0.02) if tolerance is None else tolerance
    m = report["metrics"]
    problems: List[str] = []
    for country, fields in baseline["accuracy"].items():
        for field, base in fields.items():
            cur = m["by_country"].get(country, {}).get(field)
            if cur is None or cur["accuracy"] is None:
                problems.append(f"{country}/{field}: missing from current results (baseline {base:.3f})")
            elif cur["accuracy"] < base - tol:
                problems.append(f"{country}/{field}: accuracy {cur['accuracy']:.3f} < baseline {base:.3f} - {tol}")
    for country, base in baseline.get("exact", {}).items():
        cur = m["exact_by_country"].get(country)
        if cur is None or cur["rate"] < base - tol:
            problems.append(f"{country}/exact: {None if cur is None else round(cur['rate'], 3)} < baseline {base:.3f} - {tol}")
    if m["exact_overall"]["rate"] < baseline.get("exact_overall", 0.0) - tol:
        problems.append(f"overall exact {m['exact_overall']['rate']:.3f} < baseline {baseline['exact_overall']:.3f} - {tol}")
    return problems


# --------------------------------------------------------------------------- markdown


def _pct(v: Optional[float]) -> str:
    return "-" if v is None else f"{100 * v:.1f}%"


def _row(label: str, d: Dict[str, Any]) -> str:
    return (f"| {label} | {d['n']} | {_pct(d['accuracy'])} | {_pct(d['precision'])} | "
            f"{_pct(d['ci95'][0])} - {_pct(d['ci95'][1])} |")


def to_markdown(report: Dict[str, Any]) -> str:
    m = report["metrics"]
    meta = report["corpus_meta"]
    L: List[str] = ["# Independent accuracy evaluation", ""]
    L.append(f"Corpus: {report['n_records']} OSM-derived records, {report['n_renderings']} input renderings "
             f"(seed {meta.get('seed')}). Ground truth = OpenStreetMap `addr:*` tags; NOT human-reviewed. "
             "(c) OpenStreetMap contributors, ODbL 1.0.")
    L += ["", "Accuracy = correct / labelled; precision = correct / (correct + wrong); 95% Wilson interval on accuracy.", ""]
    ex = m["exact_overall"]
    L.append(f"**All-fields exact match (all renderings): {_pct(ex['rate'])}** "
             f"({ex['exact']}/{ex['n']}, 95% CI {_pct(ex['ci95'][0])} - {_pct(ex['ci95'][1])})")
    L += ["", "## Overall by field", "", "| field | n | accuracy | precision | 95% CI |", "|---|---|---|---|---|"]
    L += [_row(f, d) for f, d in m["overall_by_field"].items()]
    L += ["", "## By country and field (accuracy, n)", "",
          "| country | exact | " + " | ".join(FIELDS) + " |", "|---|---|" + "---|" * len(FIELDS)]
    for c, fields in m["by_country"].items():
        cells = [f"{_pct(fields[f]['accuracy'])} ({fields[f]['n']})" if f in fields else "-" for f in FIELDS]
        L.append(f"| {c} | {_pct(m['exact_by_country'][c]['rate'])} | " + " | ".join(cells) + " |")
    L += ["", "## By input style and field (accuracy, n)", "",
          "| style | exact | " + " | ".join(FIELDS) + " |", "|---|---|" + "---|" * len(FIELDS)]
    for s, fields in m["by_style"].items():
        cells = [f"{_pct(fields[f]['accuracy'])} ({fields[f]['n']})" if f in fields else "-" for f in FIELDS]
        L.append(f"| {s} | {_pct(m['exact_by_style'][s]['rate'])} | " + " | ".join(cells) + " |")
    L += ["", "## Worst failures", ""]
    for w in report["worst_failures"]:
        L.append(f"- `{w['id']}` [{w['style']}] failed {sorted(w['failed'])}: input `{json.dumps(w['input'], ensure_ascii=False)}`"
                 f" -> mismatched predictions `{json.dumps(w['predicted'], ensure_ascii=False)}` (confidence {w['confidence']})")
    cal = report.get("calibration")
    if cal:
        L += ["", "## Raw confidence score vs. observed all-fields correctness", "",
              f"n = {cal['n']}, observed exact-match rate = {_pct(cal['base_rate_exact'])}, "
              f"ECE = {cal['ece']:.3f}, Brier = {cal['brier']:.3f}. The raw score is a rule-based heuristic, "
              "not a probability.", "",
              "| bin | n | mean score | observed exact |", "|---|---|---|---|"]
        for b in cal["bins"]:
            L.append(f"| [{b['lower']:.1f}, {b['upper']:.1f}) | {b['count']} | {b['mean_confidence']:.3f} | {_pct(b['accuracy'])} |")
    return "\n".join(L) + "\n"


def main(argv: Optional[List[str]] = None) -> int:  # pragma: no cover - thin CLI wrapper
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default=os.path.join(HERE, "osm_sample.json"))
    ap.add_argument("--out-json")
    ap.add_argument("--out-md")
    ap.add_argument("--baseline", help="fail (exit 1) if any (country, field) accuracy drops > tolerance")
    ap.add_argument("--tolerance", type=float, help="override the baseline file's tolerance")
    ap.add_argument("--write-baseline", help="write the current results as a new baseline file")
    args = ap.parse_args(argv)

    corpus = load_corpus(args.corpus)
    report = build_report(corpus, evaluate(corpus))
    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
    md = to_markdown(report)
    if args.out_md:
        with open(args.out_md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(md)
    else:
        print(md)
    if args.write_baseline:
        with open(args.write_baseline, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(baseline_from_report(report), fh, indent=1, sort_keys=True)
            fh.write("\n")
    if args.baseline:
        with open(args.baseline, encoding="utf-8") as fh:
            problems = check_baseline(report, json.load(fh), args.tolerance)
        if problems:
            print("BASELINE REGRESSION:\n  " + "\n  ".join(problems), file=sys.stderr)
            return 1
        print("baseline OK", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
