"""
cProfile harness for the mixed real-world hot path.
===================================================
Standardizes the first N records of a golden dataset with a cold result cache and prints the heaviest functions by
own time and by cumulative time, so optimisations start from evidence instead of guesses::

    python benchmarks/run_profile.py                       # domestic golden set, 1000 records
    python benchmarks/run_profile.py --dataset multi_national --top 40 --sort cumulative

Profiling overhead inflates absolute times roughly 2x; read the output for proportions, and use
``benchmarks/run_benchmarks.py`` for throughput.
"""

import argparse
import cProfile
import io
import json
import os
import pstats
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from address_standardizer import standardize_address  # noqa: E402
from address_standardizer.cache import clear_cache  # noqa: E402

_DATASETS = {
    "domestic": os.path.join("benchmarks", "golden_dataset.json"),
    "multi_national": os.path.join("benchmarks", "data", "golden_dataset_multinational.json"),
}


def load_items(dataset: str, limit: int):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = _DATASETS.get(dataset, dataset)
    if not os.path.isabs(path):
        path = os.path.join(root, path)
    with open(path, "r", encoding="utf-8") as handle:
        records = json.load(handle)[:limit]
    keys = ("street1", "street2", "city", "state", "postal_code", "country")
    return [tuple(r["raw_input"].get(k) for k in keys) for r in records]


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile standardize_address on a golden dataset")
    parser.add_argument("--dataset", default="domestic", help="'domestic', 'multi_national' or a JSON file path")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument("--sort", choices=["tottime", "cumulative"], default="tottime")
    args = parser.parse_args()

    items = load_items(args.dataset, args.limit)
    for item in items[:100]:  # warm imports and lazy tables so they are not attributed to the records
        standardize_address(*item)
    clear_cache()

    profiler = cProfile.Profile()
    profiler.enable()
    for item in items:
        standardize_address(*item)
    profiler.disable()

    out = io.StringIO()
    pstats.Stats(profiler, stream=out).sort_stats(args.sort).print_stats(args.top)
    print(f"{len(items)} records, sorted by {args.sort}")
    print(out.getvalue())


if __name__ == "__main__":
    main()
