# Held-out accuracy evaluation (generalisation estimate)

**This set was NOT used for development.** `osm_holdout.json` was built from city areas that are disjoint from every
bounding box in `osm_sample.json` (and with a different seed, 20261201). No engine change, comparison rule, abbreviation
table or baseline was tuned against it, and `baseline.json` is deliberately NOT written from it. Report the numbers
below as the **generalisation estimate**. The in-sample figures (`REPORT.md`, `osm_sample.json`) were used by other
agents to diagnose and fix engine failures, so they are optimistic and must not be quoted as accuracy.

Rule: holdout failures may be *read* to decide what to build next, but the holdout file is never used to tune. After a
fix is made from these findings the numbers here stop being a clean estimate for that area; refresh the holdout with new
bounding boxes (see `docs/evaluation.md`) before claiming a new generalisation number.

Caveats: OSM labels are volunteer-entered and not human-reviewed; the messy styles are synthetic; holdout-only countries
(AR, CL, CZ, EG, FI, HU, IN, MX, NO, RO, SA, SG, TR, ZA, AU) have never been looked at by anyone, so their lower numbers are
first-contact results. A few failure categories below are partly scorer limitations (French/Turkish folding), flagged there.
Hong Kong returned no tagged addresses; Saudi Arabia (6), Israel (22) and Ukraine (27) are thin. Per-country n is 30 records
(~255 renderings), so per-country intervals are still wide.

## In-sample vs holdout (engine at the time of this run; in-sample re-run today)

Differences are mostly about *which cities* were tested plus 15 countries/forms that the in-sample set never contained.
`line_swapped` in-sample is 0%; the holdout mix differs (more countries, different state-bearing records), so that row is
not comparable. "in-sample >> holdout" = in-sample exact at least 15 points higher.

| metric | in-sample | holdout | delta (pts) |
|---|---|---|---|
| **all-fields exact** | 93.7% (n=2417) | 85.4% (n=10211) | -8.3 |
| house_number | 100.0% | 96.2% | -3.8 |
| street | 94.4% | 87.8% | -6.6 |
| city | 95.2% | 89.5% | -5.7 |
| state | 95.8% | 90.8% | -5.0 |
| postcode | 97.0% | 93.3% | -3.7 |
| country | 100.0% | 100.0% | +0.0 |

| style | in-sample exact | holdout exact | delta (pts) |
|---|---|---|---|
| line | 99.6% | 90.4% | -9.3 |
| line_abbrev | 83.7% | 82.3% | -1.4 |
| line_country_text | 99.6% | 90.6% | -9.0 |
| line_lower | 99.6% | 90.4% | -9.3 |
| line_messy | 99.6% | 90.4% | -9.3 |
| line_no_postal | 99.6% | 91.7% | -7.9 |
| line_nocomma | 65.2% | 51.7% | -13.5 |
| line_swapped | 0.0% | 38.5% | +38.5 |
| line_upper | 99.6% | 90.4% | -9.3 |
| structured | 100.0% | 96.2% | -3.8 |
| structured_swapped | 0.0% | 0.0% | +0.0 |

| country | holdout records | in-sample exact | holdout exact | delta (pts) | flag |
|---|---|---|---|---|---|
| AR | 30 | - | 72.9% | - | holdout-only country |
| AT | 30 | 98.9% | 100.0% | +1.1 |  |
| AU | 30 | - | 86.1% | - | holdout-only country |
| BE | 30 | 79.5% | 79.2% | -0.3 |  |
| BR | 30 | 100.0% | 95.2% | -4.8 |  |
| CA | 30 | 84.7% | 66.8% | -17.9 | **in-sample >> holdout** |
| CH | 30 | 100.0% | 100.0% | +0.0 |  |
| CL | 30 | - | 96.8% | - | holdout-only country |
| CZ | 30 | - | 79.2% | - | holdout-only country |
| DE | 30 | 100.0% | 100.0% | +0.0 |  |
| DK | 30 | 100.0% | 100.0% | +0.0 |  |
| EG | 30 | - | 87.5% | - | holdout-only country |
| ES | 30 | 100.0% | 99.6% | -0.4 |  |
| FI | 30 | - | 100.0% | - | holdout-only country |
| FR | 30 | 100.0% | 96.7% | -3.3 |  |
| GB | 30 | 88.8% | 85.8% | -3.0 |  |
| GR | 30 | 87.5% | 87.5% | +0.0 |  |
| HU | 30 | - | 12.5% | - | holdout-only country |
| IE | 30 | 88.5% | 88.7% | +0.2 |  |
| IL | 22 | 87.5% | 87.5% | +0.0 |  |
| IN | 30 | - | 57.7% | - | holdout-only country |
| IT | 30 | 88.9% | 89.2% | +0.3 |  |
| JP | 30 | 100.0% | 21.2% | -78.8 | **in-sample >> holdout** |
| KR | 30 | 100.0% | 100.0% | +0.0 |  |
| MX | 30 | - | 85.8% | - | holdout-only country |
| NL | 30 | 97.8% | 95.6% | -2.2 |  |
| NO | 30 | - | 100.0% | - | holdout-only country |
| NZ | 30 | 88.8% | 88.8% | +0.0 |  |
| PL | 30 | 87.8% | 87.5% | -0.3 |  |
| PT | 30 | 100.0% | 94.8% | -5.2 |  |
| RO | 30 | - | 87.5% | - | holdout-only country |
| RU | 30 | 100.0% | 99.6% | -0.4 |  |
| SA | 6 | - | 87.5% | - | holdout-only country |
| SE | 30 | 100.0% | 100.0% | +0.0 |  |
| SG | 30 | - | 96.6% | - | holdout-only country |
| TH | 30 | 80.7% | 84.6% | +3.9 |  |
| TR | 30 | - | 46.7% | - | holdout-only country |
| TW | 30 | 100.0% | 100.0% | +0.0 |  |
| UA | 27 | 100.0% | 99.6% | -0.4 |  |
| US | 30 | 81.8% | 78.1% | -3.7 |  |
| ZA | 30 | - | 81.1% | - | holdout-only country |

(Failure categories with examples are at the end of this document.)

Corpus: 1195 OSM-derived records, 10211 input renderings (seed 20261201). Ground truth = OpenStreetMap `addr:*` tags; NOT human-reviewed. (c) OpenStreetMap contributors, ODbL 1.0.

Accuracy = correct / labelled; precision = correct / (correct + wrong); 95% Wilson interval on accuracy.

**All-fields exact match (all renderings): 85.4%** (8721/10211, 95% CI 84.7% - 86.1%)

## Holdout: Overall by field

| field | n | accuracy | precision | 95% CI |
|---|---|---|---|---|
| house_number | 10211 | 96.2% | 96.6% | 95.9% - 96.6% |
| street | 10211 | 87.8% | 87.8% | 87.1% - 88.4% |
| city | 10211 | 89.5% | 95.0% | 88.8% - 90.0% |
| state | 706 | 90.8% | 96.2% | 88.4% - 92.7% |
| postcode | 9016 | 93.3% | 100.0% | 92.8% - 93.8% |
| country | 10211 | 100.0% | 100.0% | 100.0% - 100.0% |

## Holdout: By country and field (accuracy, n)

| country | exact | house_number | street | city | state | postcode | country |
|---|---|---|---|---|---|---|---|
| AR | 72.9% | 100.0% (251) | 88.4% (251) | 72.9% (251) | - | 69.7% (221) | 100.0% (251) |
| AT | 100.0% | 100.0% (264) | 100.0% (264) | 100.0% (264) | - | 100.0% (234) | 100.0% (264) |
| AU | 86.1% | 100.0% (288) | 89.6% (288) | 86.1% (288) | 99.1% (110) | 100.0% (258) | 100.0% (288) |
| BE | 79.2% | 100.0% (265) | 79.2% (265) | 88.7% (265) | - | 87.2% (235) | 100.0% (265) |
| BR | 95.2% | 98.9% (272) | 100.0% (272) | 95.2% (272) | 9.1% (11) | 100.0% (242) | 100.0% (272) |
| CA | 66.8% | 100.0% (298) | 72.5% (298) | 83.2% (298) | 87.9% (215) | 100.0% (268) | 100.0% (298) |
| CH | 100.0% | 100.0% (252) | 100.0% (252) | 100.0% (252) | - | 100.0% (222) | 100.0% (252) |
| CL | 96.8% | 100.0% (249) | 96.8% (249) | 100.0% (249) | - | 100.0% (219) | 100.0% (249) |
| CZ | 79.2% | 100.0% (240) | 87.5% (240) | 79.2% (240) | - | 85.7% (210) | 100.0% (240) |
| DE | 100.0% | 100.0% (254) | 100.0% (254) | 100.0% (254) | - | 100.0% (224) | 100.0% (254) |
| DK | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| EG | 87.5% | 100.0% (240) | 87.5% (240) | 87.5% (240) | - | 85.7% (210) | 100.0% (240) |
| ES | 99.6% | 100.0% (254) | 99.6% (254) | 99.6% (254) | - | 99.6% (224) | 100.0% (254) |
| FI | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| FR | 96.7% | 100.0% (243) | 96.7% (243) | 100.0% (243) | - | 100.0% (213) | 100.0% (243) |
| GB | 85.8% | 100.0% (267) | 85.8% (267) | 88.8% (267) | - | 87.3% (237) | 100.0% (267) |
| GR | 87.5% | 100.0% (240) | 87.5% (240) | 87.5% (240) | - | 85.7% (210) | 100.0% (240) |
| HU | 12.5% | 25.0% (240) | 12.5% (240) | 12.5% (240) | - | 14.3% (210) | 100.0% (240) |
| IE | 88.7% | 100.0% (266) | 88.7% (266) | 88.7% (266) | - | 100.0% (236) | 100.0% (266) |
| IL | 87.5% | 100.0% (176) | 87.5% (176) | 87.5% (176) | - | 85.7% (154) | 100.0% (176) |
| IN | 57.7% | 96.6% (265) | 77.4% (265) | 60.8% (265) | 100.0% (10) | 97.0% (235) | 100.0% (265) |
| IT | 89.2% | 100.0% (269) | 89.2% (269) | 100.0% (269) | - | 100.0% (239) | 100.0% (269) |
| JP | 21.2% | 27.5% (240) | 21.2% (240) | 68.8% (240) | - | 95.2% (210) | 100.0% (240) |
| KR | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| MX | 85.8% | 100.0% (267) | 95.5% (267) | 94.8% (267) | 9.7% (31) | 99.6% (237) | 100.0% (267) |
| NL | 95.6% | 100.0% (251) | 95.6% (251) | 100.0% (251) | - | 100.0% (221) | 100.0% (251) |
| NO | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| NZ | 88.8% | 100.0% (268) | 88.8% (268) | 88.8% (268) | - | 87.4% (238) | 100.0% (268) |
| PL | 87.5% | 100.0% (240) | 87.5% (240) | 87.5% (240) | - | 100.0% (210) | 100.0% (240) |
| PT | 94.8% | 100.0% (269) | 99.3% (269) | 94.8% (269) | - | 94.1% (239) | 100.0% (269) |
| RO | 87.5% | 100.0% (240) | 87.5% (240) | 87.5% (240) | - | 85.7% (210) | 100.0% (240) |
| RU | 99.6% | 100.0% (269) | 99.6% (269) | 100.0% (269) | - | 100.0% (239) | 100.0% (269) |
| SA | 87.5% | 100.0% (48) | 87.5% (48) | 87.5% (48) | - | 85.7% (42) | 100.0% (48) |
| SE | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| SG | 96.6% | 96.6% (268) | 96.6% (268) | 100.0% (268) | - | 100.0% (238) | 100.0% (268) |
| TH | 84.6% | 96.7% (240) | 85.4% (240) | 85.0% (240) | - | 86.2% (210) | 100.0% (240) |
| TR | 46.7% | 100.0% (240) | 46.7% (240) | 87.5% (240) | - | 85.7% (210) | 100.0% (240) |
| TW | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| UA | 99.6% | 100.0% (239) | 99.6% (239) | 99.6% (239) | - | 100.0% (212) | 100.0% (239) |
| US | 78.1% | 100.0% (329) | 87.2% (329) | 84.2% (329) | 100.0% (329) | 100.0% (299) | 100.0% (329) |
| ZA | 81.1% | 100.0% (270) | 88.9% (270) | 81.1% (270) | - | 88.8% (240) | 100.0% (270) |

## Holdout: By input style and field (accuracy, n)

| style | exact | house_number | street | city | state | postcode | country |
|---|---|---|---|---|---|---|---|
| line | 90.4% | 95.3% (1195) | 92.6% (1195) | 94.1% (1195) | 93.8% (65) | 96.5% (1195) | 100.0% (1195) |
| line_abbrev | 82.3% | 99.6% (521) | 85.0% (521) | 96.7% (521) | 96.4% (56) | 98.8% (521) | 100.0% (521) |
| line_country_text | 90.6% | 95.4% (1195) | 92.9% (1195) | 94.1% (1195) | 93.8% (65) | 96.7% (1195) | 100.0% (1195) |
| line_lower | 90.4% | 95.3% (1195) | 92.6% (1195) | 94.1% (1195) | 93.8% (65) | 96.5% (1195) | 100.0% (1195) |
| line_messy | 90.4% | 95.3% (1195) | 92.6% (1195) | 94.1% (1195) | 93.8% (65) | 96.5% (1195) | 100.0% (1195) |
| line_no_postal | 91.7% | 95.4% (1195) | 93.0% (1195) | 95.2% (1195) | 93.8% (65) | - | 100.0% (1195) |
| line_nocomma | 51.7% | 97.6% (1195) | 52.6% (1195) | 53.4% (1195) | 89.2% (65) | 67.4% (1195) | 100.0% (1195) |
| line_swapped | 38.5% | 100.0% (65) | 44.6% (65) | 58.5% (65) | 89.2% (65) | 100.0% (65) | 100.0% (65) |
| line_upper | 90.4% | 95.3% (1195) | 92.6% (1195) | 94.1% (1195) | 93.8% (65) | 96.5% (1195) | 100.0% (1195) |
| structured | 96.2% | 98.5% (1195) | 96.4% (1195) | 100.0% (1195) | 100.0% (65) | 100.0% (1195) | 100.0% (1195) |
| structured_swapped | 0.0% | 100.0% (65) | 93.8% (65) | 0.0% (65) | 61.5% (65) | 100.0% (65) | 100.0% (65) |

## Holdout: Worst failures

- `HU-n2460128429` [line] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "HU", "street1": "4029 Debrecen, Csapó utca 22"}` -> mismatched predictions `{"house_number": "4029 DEBRECEN", "street": "4029 DEBRECEN", "city": "CSAPÓ UTCA 22", "postcode": ""}` (confidence 0.985)
- `HU-n2460128429` [line_country_text] failed ['city', 'house_number', 'postcode', 'street']: input `{"street1": "4029 Debrecen, Csapó utca 22, Hungary"}` -> mismatched predictions `{"house_number": "4029 DEBRECEN", "street": "4029 DEBRECEN", "city": "CSAPÓ UTCA 22", "postcode": ""}` (confidence 0.985)
- `HU-n2460128429` [line_lower] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "HU", "street1": "4029 debrecen, csapó utca 22"}` -> mismatched predictions `{"house_number": "4029 DEBRECEN", "street": "4029 DEBRECEN", "city": "CSAPÓ UTCA 22", "postcode": ""}` (confidence 0.985)
- `HU-n2460128429` [line_messy] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "HU", "street1": " 4029 Debrecen, Csapó utca 22 "}` -> mismatched predictions `{"house_number": "4029 DEBRECEN", "street": "4029 DEBRECEN", "city": "CSAPÓ UTCA 22", "postcode": ""}` (confidence 0.985)
- `HU-n2460128429` [line_upper] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "HU", "street1": "4029 DEBRECEN, CSAPÓ UTCA 22"}` -> mismatched predictions `{"house_number": "4029 DEBRECEN", "street": "4029 DEBRECEN", "city": "CSAPÓ UTCA 22", "postcode": ""}` (confidence 0.985)
- `HU-n2460128464` [line] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "HU", "street1": "4026 Debrecen, Péterfia utca 30a"}` -> mismatched predictions `{"house_number": "4026 DEBRECEN", "street": "4026 DEBRECEN", "city": "PÉTERFIA UTCA 30A", "postcode": ""}` (confidence 0.985)
- `HU-n2460128464` [line_country_text] failed ['city', 'house_number', 'postcode', 'street']: input `{"street1": "4026 Debrecen, Péterfia utca 30a, Hungary"}` -> mismatched predictions `{"house_number": "4026 DEBRECEN", "street": "4026 DEBRECEN", "city": "PÉTERFIA UTCA 30A", "postcode": ""}` (confidence 0.985)
- `HU-n2460128464` [line_lower] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "HU", "street1": "4026 debrecen, péterfia utca 30a"}` -> mismatched predictions `{"house_number": "4026 DEBRECEN", "street": "4026 DEBRECEN", "city": "PÉTERFIA UTCA 30A", "postcode": ""}` (confidence 0.985)
- `HU-n2460128464` [line_messy] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "HU", "street1": " 4026 Debrecen, Péterfia utca 30a "}` -> mismatched predictions `{"house_number": "4026 DEBRECEN", "street": "4026 DEBRECEN", "city": "PÉTERFIA UTCA 30A", "postcode": ""}` (confidence 0.985)
- `HU-n2460128464` [line_upper] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "HU", "street1": "4026 DEBRECEN, PÉTERFIA UTCA 30A"}` -> mismatched predictions `{"house_number": "4026 DEBRECEN", "street": "4026 DEBRECEN", "city": "PÉTERFIA UTCA 30A", "postcode": ""}` (confidence 0.985)
- `JP-n2071427058` [line] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "8120011 福岡市 祇園町2-1"}` -> mismatched predictions `{"house_number": "福岡市 8120011", "street": "福岡市 8120011", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n2071427058` [line_lower] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "8120011 福岡市 祇園町2-1"}` -> mismatched predictions `{"house_number": "福岡市 8120011", "street": "福岡市 8120011", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n2071427058` [line_messy] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": " 8120011 \t福岡市 \t祇園町2-1"}` -> mismatched predictions `{"house_number": "福岡市 8120011", "street": "福岡市 8120011", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n2071427058` [line_nocomma] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "8120011 福岡市 祇園町2-1"}` -> mismatched predictions `{"house_number": "福岡市 8120011", "street": "福岡市 8120011", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n2071427058` [line_upper] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "8120011 福岡市 祇園町2-1"}` -> mismatched predictions `{"house_number": "福岡市 8120011", "street": "福岡市 8120011", "city": "", "postcode": ""}` (confidence 0.94)

## Holdout: Raw confidence score vs. observed all-fields correctness

n = 10211, observed exact-match rate = 85.4%, ECE = 0.127, Brier = 0.135. The raw score is a rule-based heuristic, not a probability.

| bin | n | mean score | observed exact |
|---|---|---|---|
| [0.0, 0.1) | 7 | 0.000 | 0.0% |
| [0.8, 0.9) | 60 | 0.880 | 50.0% |
| [0.9, 1.0) | 10144 | 0.982 | 85.7% |

## Top failure categories (observed, NOT fixed)

Counted on the three realistic styles only (`structured`, `line`, `line_messy`: 3,585 renderings, 275 not exact),
so the deliberate stress styles (`line_nocomma`, `structured_swapped`, `line_swapped`) do not drown the signal.
Counts are failing renderings. No engine change was made in response to these.

1. **Hungarian postcode-first lines are not parsed at all (HU, 60 renderings, ~100% of HU one-line input).**
   `"{pc} {city}, {street} {number}"` leaves the postcode empty, puts `1054 BUDAPEST` in street/house number and the
   street into city.
   - HU `1054 Budapest, Zoltán utca 16` -> house_number `1054 BUDAPEST`, city `ZOLTÁN UTCA 16`, postcode empty
   - HU `1051 Budapest, Nádor utca 29` -> same pattern
   - HU `1071 Budapest, Damjanich utca 14` -> same pattern
2. **Japanese one-line input: house number glued to the street, ward/city split wrong (JP, 66 renderings; in-sample 100%, holdout
   21% exact).** The sample's JP boxes (Tokyo/Osaka) were fixed; Fukuoka, Sapporo and Nagoya shapes are not handled.
   Block numbers and `丁目` forms are not separated, and `市 区` pairs are assigned to the wrong fields.
   - JP `810-0021 福岡市 中央区 今泉1-18-25` -> city `中央区` (label `福岡市`), street `今泉 1-18-25`
   - JP `060-0001 札幌市 北１条西17丁目16` -> house_number/street both `北1条西 17丁目16`
   - JP `461-0011 名古屋市東区白壁 出来町通4-63-3` -> house_number `出来町通4-63-3 東区白壁`
3. **Postcode glued to the city is not split when the postcode is not purely numeric, or is a short code (AR, PT, CZ, plus 4-digit
   cases).** The `{pc} {city}` token stays in `city` and postcode is empty.
   - AR `Avenida Hipólito Yrigoyen 584, X5000 Córdoba` -> city `X5000 CÓRDOBA`, postcode empty (letter-prefixed CPA code)
   - AR `Avenida Marcelo T. de Alvear 488, 500 Córdoba` -> city `500 CÓRDOBA`
   - PT `Rua da Alegria 946, 4000 Porto` -> city `4000 PORTO` (4-digit-only PT postcode, Porto boxes)
   - CZ `Bílkova 132/4, 11000 Praha 1` -> city `11000 PRAHA 1` (postcode captured, city keeps the digits; 8 renderings)
4. **Turkish street names (TR, 42 renderings; probably partly a scorer artefact).** Output is upper-cased and `ı`/`I` collapse
   (`Kızılırmak Caddesi` -> `KIZILIRMAK CADDESI`); the harness fold keeps dotless `ı` distinct from `i`, so the street counts as wrong.
   Worth checking whether the engine should preserve Turkish case (`ı`/`İ`) or the scorer should fold it before treating as an engine bug.
   - TR `Kızılırmak Caddesi 13 / 4, 06420 Ankara` -> street `KIZILIRMAK CADDESI 13 / 4`
   - TR `Turnacıbaşı Sokak 41, 34433 İstanbul` -> `TURNACIBAŞI SOKAK 41`
   - TR `Şair Eşref Bulvarı 63, 35220 İzmir` -> `ŞAIR EŞREF BULVARI 63`
5. **Locality / sub-locality kept in the city label but engine returns only the last element (ZA, MX, IN, BR, TH).**
   Partly a label-convention problem, but the engine also drops or mis-assigns state.
   - ZA `176 Sir Lowry Road, Woodstock, Cape Town, 8001` -> city `CAPE TOWN` (label `Woodstock, Cape Town`)
   - IN `41 Outer Circle, New Delhi 110001` -> city empty (`New Delhi` is not recognised as a city when directly followed by the PIN); 10 city-missing, 12 city-wrong in IN
   - MX `Calle Joaquín Angulo 1029, 44200 Guadalajara` -> state `Jalisco` label never produced (6 state-missing)
   - BR `Rua Emiliano Perneta, 860, Curitiba - Paraná, 80420-080` -> city `CURITIBA - PARANÁ`, state empty (hyphen-separated state, outside the in-sample cities)
   - TH `217/27 Moo 9 Beach Rd., Nongprue, Banglamung, Chonburi 20150` -> `Moo 9` / sub-district folded into house number/street
6. **French-Canadian streets: directional `Ouest`/`Est` abbreviated to `O`/`E` (CA, Montréal, 18 renderings; likely scorer limitation).**
   Canada Post abbreviates them, but the harness's directional table has no French entries, so they count as wrong.
   - CA `9 Avenue Viger Ouest, Montréal, QC H2Z 1E6` -> `9 AV VIGER O`
   - CA `1345 Rue Ontario Est, Montréal, QC H2L 1R9` -> `1345 RUE ONTARIO E`
   - Same cause explains in-sample CA 84.7% vs holdout 66.8% (the sample's Toronto/Ottawa boxes have few French streets).
7. **English named-highway forms and `North ...` names mis-expanded (US, GB; small).**
   - US `82 North Interstate Highway 35 Service Road, Austin, TX 78701` -> `82 N INTERSTATE HIGHWAY 35TH SERVICE RD` (invented ordinal `35TH`)
   - GB `3 North Western Arcade, Birmingham, B2 5LH` -> `3 N WESTERN ARC` (`North` is read as a directional on a named street)
8. **Lines without separators (all countries, `line_nocomma`): 51.8% exact** versus 65.2% in-sample; engine still needs commas. Known and deliberate stress style,
   not a new finding, but it is the single largest source of non-exact renderings overall. `structured_swapped` remains 0%
   (also known; the engine does not repair swapped city/state fields).

Not buildable / thin: Hong Kong yielded zero tagged addresses (HK rarely has `addr:postcode`), Saudi Arabia only 6 records and Israel 22,
Ukraine 27 (thin OSM tagging); see the corpus section below. Several Overpass bounding boxes returned HTTP 500/504 on earlier passes
and were retried until they succeeded (the final build had no skipped boxes).
