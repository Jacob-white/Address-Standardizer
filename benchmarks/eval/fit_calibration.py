"""
Fit a confidence calibrator from evaluation results.
====================================================
Reads either a results JSON written by ``run_eval.py --out-json`` or runs the evaluation on a corpus, then:

1. splits records deterministically (by a hash of the record id) into train/held-out halves,
2. fits an isotonic calibrator on the train half and reports raw vs calibrated ECE/Brier on the HELD-OUT half
   (the honest estimate), and
3. fits the final calibrator on all rows and writes it (default benchmarks/eval/calibration.json), plus a
   markdown reliability report.

The "was correct" label is all-fields exact match against the OSM ground truth. The raw composite score is a
rule-based heuristic; this calibrator maps it to the observed exact-match rate on THIS sample only. It is
not a general guarantee and must be refit on data resembling production before being relied upon.

    PYTHONPATH=. python benchmarks/eval/fit_calibration.py --corpus benchmarks/eval/osm_sample.json
"""

import argparse
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from address_standardizer.calibration import (  # noqa: E402
    brier_score,
    expected_calibration_error,
    fit_isotonic,
    reliability_bins,
)
from benchmarks.eval import run_eval  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
Pair = Tuple[float, bool]


def split_pairs(rows: List[Dict[str, Any]]) -> Tuple[List[Pair], List[Pair]]:
    """Deterministic train/held-out split keyed on the record id (all renderings of a record stay together)."""
    train: List[Pair] = []
    test: List[Pair] = []
    for r in rows:
        bucket = hashlib.sha1(r["id"].encode("utf-8")).digest()[0] & 1
        (train if bucket == 0 else test).append((r["confidence"], bool(r["exact"])))
    return train, test


def _stats(pairs: List[Pair], mapper: Any = None) -> Dict[str, float]:
    mapped = pairs if mapper is None else [(mapper(s), ok) for s, ok in pairs]
    return {"n": len(mapped), "ece": expected_calibration_error(mapped), "brier": brier_score(mapped)}


def fit_and_report(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return {'calibrator', 'held_out': {...}, 'bins': [...], 'base_rate': float}."""
    if not rows:
        raise ValueError("no evaluation rows to fit a calibrator on")
    all_pairs: List[Pair] = [(r["confidence"], bool(r["exact"])) for r in rows]
    train, test = split_pairs(rows)
    held: Optional[Dict[str, Any]] = None
    if train and test:
        cal_train = fit_isotonic(train)
        held = {"raw": _stats(test), "calibrated": _stats(test, cal_train.calibrate), "n_train": len(train)}
    final = fit_isotonic(all_pairs)
    return {
        "calibrator": final,
        "held_out": held,
        "in_sample": {"raw": _stats(all_pairs), "calibrated": _stats(all_pairs, final.calibrate)},
        "base_rate": sum(ok for _, ok in all_pairs) / len(all_pairs),
        "bins": [b.as_dict() for b in reliability_bins(all_pairs)],
    }


def to_markdown(res: Dict[str, Any]) -> str:
    L = ["# Confidence calibration on the OSM sample", "",
         f"Observed all-fields exact-match rate: {100 * res['base_rate']:.1f}%.", ""]
    ho = res["held_out"]
    if ho:
        L += ["Held-out half (fit on a disjoint half of the records, split by record id):", "",
              "| score | n | ECE | Brier |", "|---|---|---|---|",
              f"| raw composite | {ho['raw']['n']} | {ho['raw']['ece']:.3f} | {ho['raw']['brier']:.3f} |",
              f"| isotonic-calibrated | {ho['calibrated']['n']} | {ho['calibrated']['ece']:.3f} | "
              f"{ho['calibrated']['brier']:.3f} |", ""]
    ins = res["in_sample"]
    L += [f"In-sample (optimistic for the calibrator): raw ECE {ins['raw']['ece']:.3f} / Brier {ins['raw']['brier']:.3f}; "
          f"calibrated ECE {ins['calibrated']['ece']:.3f} / Brier {ins['calibrated']['brier']:.3f}.", "",
          "## Reliability table (raw score, all rows)", "",
          "| bin | n | mean score | observed exact | gap |", "|---|---|---|---|---|"]
    for b in res["bins"]:
        L.append(f"| [{b['lower']:.1f}, {b['upper']:.1f}) | {b['count']} | {b['mean_confidence']:.3f} | "
                 f"{100 * b['accuracy']:.1f}% | {b['accuracy'] - b['mean_confidence']:+.3f} |")
    L += ["", "The raw score is a heuristic, not a probability; this table shows how far it is from one on this sample."]
    return "\n".join(L) + "\n"


def main(argv: Optional[List[str]] = None) -> int:  # pragma: no cover - thin CLI wrapper
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--results", help="JSON from run_eval.py --out-json")
    src.add_argument("--corpus", default=os.path.join(HERE, "osm_sample.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "calibration.json"))
    ap.add_argument("--out-md", help="write the reliability report here (default: print)")
    args = ap.parse_args(argv)

    if args.results:
        with open(args.results, encoding="utf-8") as fh:
            rows = json.load(fh)["rows"]
    else:
        corpus = run_eval.load_corpus(args.corpus)
        rows = run_eval.evaluate(corpus)
    res = fit_and_report(rows)
    res["calibrator"].save(args.out)
    md = to_markdown(res)
    if args.out_md:
        with open(args.out_md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(md)
    else:
        print(md)
    print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
