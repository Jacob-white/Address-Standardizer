"""The committed golden datasets must be exactly what their generators produce (no hand-edited drift)."""

import json
from pathlib import Path

from benchmarks.generate_golden_dataset import build_golden_dataset
from benchmarks.generate_multinational_golden_dataset import generate_multinational_golden_dataset

BENCH = Path(__file__).resolve().parent.parent / "benchmarks"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_domestic_generator_reproduces_committed_datasets():
    generated = json.loads(json.dumps(build_golden_dataset()))
    assert generated == _load(BENCH / "golden_dataset.json")
    assert generated == _load(BENCH / "data" / "golden_evaluation_dataset.json")


def test_multinational_generator_reproduces_committed_dataset():
    generated = json.loads(json.dumps(generate_multinational_golden_dataset(), ensure_ascii=False))
    assert generated == _load(BENCH / "data" / "golden_dataset_multinational.json")
