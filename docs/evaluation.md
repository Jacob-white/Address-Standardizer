# Independent accuracy evaluation

The golden datasets under `benchmarks/` are generated from this engine's own templates and reviewed overrides, so a
100% result there means "no regression", not "accurate on real addresses". This page describes the **independent**
evaluation harness under `benchmarks/eval/`, whose ground truth comes from outside the engine.

## How ground truth is obtained

1. `benchmarks/eval/build_osm_corpus.py` queries the OpenStreetMap Overpass API for objects (nodes, ways,
   relations) inside small, configurable bounding boxes per country. An object qualifies when it carries
   `addr:housenumber`, `addr:street`, `addr:postcode` and `addr:city`; `addr:state` (or `addr:province`) is kept when
   present.
2. Those structured tags are the **labels**: `house_number`, `street`, `city`, `state`, `postcode`, plus the country
   (from the bounding-box configuration). Multi-valued or implausible tags (`12;14`, very long names) are dropped.
3. For each record the builder renders several **inputs** with seeded, deterministic string transformations that
   never call the engine (the module does not import it, and a test enforces that):

   | style | what it does |
   |---|---|
   | `structured` | separate street1 / city / state / postal_code / country fields in local order |
   | `structured_swapped` | city and state values swapped between their fields (needs a state label) |
   | `line` | one line in local order with commas; country passed as an ISO code |
   | `line_country_text` | like `line` but the country name is appended and no country parameter is given |
   | `line_nocomma` | one line without commas |
   | `line_upper`, `line_lower` | ALL CAPS and lowercase |
   | `line_abbrev` | street types/directionals abbreviated (per-language table; skipped when nothing abbreviates) |
   | `line_no_postal` | postal code removed from the input (the postcode field is then not scored) |
   | `line_swapped` | city and state swapped inside the line |
   | `line_messy` | extra/odd whitespace (NBSP, tabs), NFD-decomposed accents, curly apostrophes, odd hyphens |

4. Responses from Overpass are cached on disk (`benchmarks/eval/.cache`, git-ignored). The builder sends a
   descriptive `User-Agent` with the project URL, sleeps between requests, retries with back-off across the
   `overpass-api.de` and `overpass.kumi.systems` endpoints, and uses small bounding boxes and result limits.

Rebuild (needs network the first time; later runs are offline from the cache):

```bash
PYTHONPATH=. python benchmarks/eval/build_osm_corpus.py --per-country 12 --seed 20261009 \
    --out benchmarks/eval/osm_sample.json
PYTHONPATH=. python benchmarks/eval/build_osm_corpus.py --offline ...   # cache only
```

Data is (c) OpenStreetMap contributors under the ODbL 1.0. See `benchmarks/eval/DATA_LICENSE.md`.
The committed `osm_sample.json` is **OSM-derived and not human-reviewed**.

## Running the evaluation

```bash
PYTHONPATH=. python benchmarks/eval/run_eval.py --corpus benchmarks/eval/osm_sample.json \
    --out-json eval.json --out-md eval.md
# regression gate against the committed baseline (exit 1 if any country/field accuracy drops > tolerance)
PYTHONPATH=. python benchmarks/eval/run_eval.py --baseline benchmarks/eval/baseline.json
# after an intentional, understood change: record a new snapshot
PYTHONPATH=. python benchmarks/eval/run_eval.py --write-baseline benchmarks/eval/baseline.json
```

`tests/test_eval_runner.py::test_committed_sample_meets_baseline` runs the same gate in CI.
**The baseline is a snapshot of current behaviour, not a target. Do not tune the engine to the sample.**

### Comparison rules

Comparisons are deliberately lenient only where the same address can legitimately be written differently:

- case, accents/diacritics and punctuation are ignored (`ß` = `ss`, NFKC/NFKD folding);
- street types and directionals are canonicalised (`St`/`Street`, `Str.`/`straße`, `N`/`North`, `Av.`/`Avenida`,
  `ул.`/`улица` ...) and English ordinal words (`Fifth` = `5th`);
- the house number is correct when its alphanumeric form appears as a whole token (or adjacent tokens) of the
  engine's street line; `12` does not match `123`;
- postal codes ignore spaces/hyphens/case; a US ZIP+4 matches its ZIP5;
- US/Canadian/Australian state names and abbreviations are equivalent;
- the country is compared as ISO 3166-1 alpha-3.

Everything else is a strict token comparison, so a missing locality word or a transliteration counts as wrong.

## Reading the report

- **Per field**: `accuracy` = correct / labelled (equal to recall); `precision` = correct / (correct + wrong), i.e.
  among values the engine actually produced; the 95% **Wilson** interval is on accuracy. A field is only scored
  when the label has a value and the input style kept it.
- **exact-match**: all scored fields of a rendering correct at once.
- **By country / by style**: use these to see where the engine fails, not the single headline number. Samples per
  country are small (a dozen records), so intervals are wide.
- **Worst failures**: renderings with the most wrong fields, with input and mismatching output, for triage. Always
  check whether the OSM label or the engine is wrong before changing code.
- **Calibration**: raw composite confidence versus observed exact-match (below).

## Confidence calibration

`address_standardizer/calibration.py` provides reliability bins, Expected Calibration Error (ECE, 10 equal-width
bins), the Brier score and a pure-Python isotonic (pool-adjacent-violators) `Calibrator` with `save`/`load`/`calibrate`.
Default behaviour of the confidence scorer is unchanged; to opt in:

```python
from address_standardizer.calibration import Calibrator
from address_standardizer.confidence import compute_confidence_score
cal = Calibrator.load("benchmarks/eval/calibration.json")
result = compute_confidence_score(std, raw_input=raw, calibrator=cal)   # result.calibrated_score
```

`benchmarks/eval/fit_calibration.py` fits it from evaluation rows (all-fields exact match is the "correct" label),
reports raw vs calibrated ECE/Brier on a held-out half split by record id, and writes `calibration.json`.
The raw score is a rule-based heuristic and was never trained to be a probability; see the measured numbers in the
section below. A calibrator fitted on this OSM sample reflects this sample's mix of countries and styles only and must
be refitted on data resembling production before its output is read as a probability.

## What "accuracy" does and does not mean

Does mean: on addresses that real mappers entered into OSM, and on mechanically degraded renderings of them, how
often the engine's fields agree with OSM's tags under the rules above.

Does not mean:

- **Not a delivery guarantee.** Nothing here checks that mail reaches the place; there is no postal authority check.
- **Labels are noisy.** OSM is volunteer data: typos, local abbreviations, inconsistent state/city usage, and
  addresses that are valid but written differently from the label. Some "errors" are label errors. The sample is
  not human-reviewed.
- **Sampling bias.** Addresses come from a few city bounding boxes chosen by hand, from objects that happen to be
  fully tagged (and Overpass returns the lowest ids first). Rural, informal and multi-unit addresses are
  under-represented. Countries are not weighted by population.
- **Synthetic degradation.** The messy styles are my model of mess, not observed production mess.
- **Country given.** Most styles pass the country as an ISO code, which makes the country field trivial; only
  `line_country_text` tests recognising it from text.
- **Small n.** About a dozen records per country; per-country numbers carry wide intervals.
- **Fields the engine does not model** (for example OSM `addr:suburb`, block/neighbourhood hierarchies in Japan or
  Korea) are not scored.

## Measured results (committed sample, 2026-10-09)

Full tables: `benchmarks/eval/REPORT.md`. Sample: 282 records from 26 countries (Latin, Cyrillic, Greek, Hebrew, Thai,
Japanese, Korean and Han scripts), 2,417 renderings. Pulled live from Overpass on 2026-10-09; some bounding boxes
returned HTTP 500/timeouts and were skipped, and Australia yielded too few tagged addresses to include.

| field | accuracy | 95% CI |
|---|---|---|
| house_number | 79.9% | 78.2 - 81.4 |
| street | 72.2% | 70.4 - 74.0 |
| city | 71.9% | 70.1 - 73.7 |
| state (where labelled) | 87.4% | 81.0 - 91.9 |
| postcode | 87.1% | 85.6 - 88.5 |
| country (mostly given) | 100% | 99.8 - 100 |
| **all fields exact** | **64.2%** | 62.2 - 66.1 |

Per style the picture is very uneven: structured input 91.8% exact, one-line with commas 71.3%, no-comma lines 3.2%
(the engine needs separators; this style is deliberately harsh), swapped city/state 0% (stress test).
Per country, Latin-script Western European countries sit near 87-89% exact (the remainder is the no-comma and
swapped stress styles), while Japan, Taiwan, Korea, Russia and Ukraine are near 0-12% on one-line input (the
engine's comma/word-order assumptions fail there), Brazil's `street, number, city` order mis-assigns the number to
the city, Dutch unspaced postcodes (`1012AP`) leak into the city, and several US ZIPs in Dorchester resolve to
WORCESTER. These are engine findings, but see the limits above before treating any single number as a verdict.

Raw confidence calibration: the composite score is essentially three clusters (0.0, ~0.88, ~0.98). Over all
renderings ECE = 0.310 and Brier = 0.310: the score reads 0.98 while the observed all-fields exact-match rate in that
bin is 66.2%. It does not discriminate well among the high-scoring renderings. An isotonic calibrator fitted on one half of the records
reduces held-out ECE from 0.289 to 0.048 (Brier 0.289 to 0.150), but most of that gain is learning the sample's base rate,
and it depends on the style mix (about one rendering in eight is a no-comma or swapped stress style). Treat `calibration.json` as a
demonstration of the mechanism, not a production calibrator.
