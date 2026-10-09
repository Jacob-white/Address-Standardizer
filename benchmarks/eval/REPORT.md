# Independent accuracy evaluation

Corpus: 282 OSM-derived records, 2417 input renderings (seed 20261009). Ground truth = OpenStreetMap `addr:*` tags; NOT human-reviewed. (c) OpenStreetMap contributors, ODbL 1.0.

Accuracy = correct / labelled; precision = correct / (correct + wrong); 95% Wilson interval on accuracy.

**All-fields exact match (all renderings): 64.2%** (1551/2417, 95% CI 62.2% - 66.1%)

## Overall by field

| field | n | accuracy | precision | 95% CI |
|---|---|---|---|---|
| house_number | 2417 | 79.9% | 91.8% | 78.2% - 81.4% |
| street | 2417 | 72.2% | 74.2% | 70.4% - 74.0% |
| city | 2417 | 71.9% | 81.6% | 70.1% - 73.7% |
| state | 143 | 87.4% | 98.4% | 81.0% - 91.9% |
| postcode | 2135 | 87.1% | 99.8% | 85.6% - 88.5% |
| country | 2417 | 100.0% | 100.0% | 99.8% - 100.0% |

## By country and field (accuracy, n)

| country | exact | house_number | street | city | state | postcode | country |
|---|---|---|---|---|---|---|---|
| AT | 87.1% | 100.0% (93) | 87.1% (93) | 88.2% (93) | - | 86.6% (82) | 100.0% (93) |
| BE | 79.5% | 100.0% (88) | 79.5% (88) | 88.6% (88) | - | 87.2% (78) | 100.0% (88) |
| BR | 11.1% | 18.2% (99) | 100.0% (99) | 88.9% (99) | - | 88.6% (88) | 100.0% (99) |
| CA | 72.4% | 100.0% (98) | 74.5% (98) | 74.5% (98) | 18.2% (22) | 100.0% (87) | 100.0% (98) |
| CH | 88.5% | 100.0% (96) | 88.5% (96) | 88.5% (96) | - | 87.1% (85) | 100.0% (96) |
| DE | 88.8% | 100.0% (98) | 88.8% (98) | 88.8% (98) | - | 87.4% (87) | 100.0% (98) |
| DK | 87.5% | 100.0% (88) | 87.5% (88) | 87.5% (88) | - | 85.7% (77) | 100.0% (88) |
| ES | 88.0% | 100.0% (92) | 88.0% (92) | 88.0% (92) | - | 86.4% (81) | 100.0% (92) |
| FR | 87.8% | 100.0% (90) | 87.8% (90) | 87.8% (90) | - | 86.1% (79) | 100.0% (90) |
| GB | 88.8% | 100.0% (98) | 88.8% (98) | 88.8% (98) | - | 87.4% (87) | 100.0% (98) |
| GR | 87.5% | 100.0% (88) | 87.5% (88) | 87.5% (88) | - | 85.7% (77) | 100.0% (88) |
| IE | 88.5% | 100.0% (96) | 88.5% (96) | 100.0% (96) | - | 100.0% (85) | 100.0% (96) |
| IL | 87.5% | 100.0% (88) | 87.5% (88) | 87.5% (88) | - | 85.7% (77) | 100.0% (88) |
| IT | 77.8% | 100.0% (99) | 77.8% (99) | 88.9% (99) | - | 87.5% (88) | 100.0% (99) |
| JP | 0.0% | 0.0% (64) | 0.0% (64) | 89.1% (64) | - | 87.5% (56) | 100.0% (64) |
| KR | 12.5% | 25.0% (88) | 12.5% (88) | 12.5% (88) | - | 100.0% (77) | 100.0% (88) |
| NL | 22.2% | 92.2% (90) | 77.8% (90) | 24.4% (90) | - | 86.1% (79) | 100.0% (90) |
| NZ | 88.8% | 100.0% (98) | 88.8% (98) | 88.8% (98) | - | 87.4% (87) | 100.0% (98) |
| PL | 78.9% | 100.0% (90) | 87.8% (90) | 78.9% (90) | - | 89.9% (79) | 100.0% (90) |
| PT | 69.1% | 91.8% (97) | 81.4% (97) | 76.3% (97) | - | 73.3% (86) | 100.0% (97) |
| RU | 11.5% | 11.5% (96) | 11.5% (96) | 11.5% (96) | - | 87.1% (85) | 100.0% (96) |
| SE | 87.5% | 100.0% (88) | 87.5% (88) | 87.5% (88) | - | 85.7% (77) | 100.0% (88) |
| TH | 80.7% | 100.0% (88) | 81.8% (88) | 80.7% (88) | - | 87.0% (77) | 100.0% (88) |
| TW | 0.0% | 0.0% (88) | 0.0% (88) | 12.5% (88) | - | 45.5% (77) | 100.0% (88) |
| UA | 11.2% | 11.2% (98) | 11.2% (98) | 11.2% (98) | - | 87.4% (87) | 100.0% (98) |
| US | 66.1% | 100.0% (121) | 93.4% (121) | 66.9% (121) | 100.0% (121) | 100.0% (110) | 100.0% (121) |

## By input style and field (accuracy, n)

| style | exact | house_number | street | city | state | postcode | country |
|---|---|---|---|---|---|---|---|
| line | 71.3% | 77.0% (282) | 79.8% (282) | 78.4% (282) | 84.6% (13) | 97.2% (282) | 100.0% (282) |
| line_abbrev | 57.0% | 77.8% (135) | 68.1% (135) | 80.7% (135) | 84.6% (13) | 99.3% (135) | 100.0% (135) |
| line_country_text | 71.3% | 80.9% (282) | 79.8% (282) | 78.4% (282) | 84.6% (13) | 97.2% (282) | 100.0% (282) |
| line_lower | 71.3% | 77.0% (282) | 79.8% (282) | 78.4% (282) | 84.6% (13) | 97.2% (282) | 100.0% (282) |
| line_messy | 66.7% | 79.8% (282) | 80.1% (282) | 70.9% (282) | 84.6% (13) | 86.2% (282) | 100.0% (282) |
| line_no_postal | 75.9% | 77.0% (282) | 80.9% (282) | 83.3% (282) | 100.0% (13) | - | 100.0% (282) |
| line_nocomma | 3.2% | 77.3% (282) | 7.8% (282) | 9.9% (282) | 84.6% (13) | 28.0% (282) | 100.0% (282) |
| line_swapped | 0.0% | 100.0% (13) | 23.1% (13) | 23.1% (13) | 84.6% (13) | 100.0% (13) | 100.0% (13) |
| line_upper | 71.3% | 77.0% (282) | 79.8% (282) | 78.4% (282) | 84.6% (13) | 97.2% (282) | 100.0% (282) |
| structured | 91.8% | 92.6% (282) | 92.6% (282) | 99.3% (282) | 100.0% (13) | 100.0% (282) | 100.0% (282) |
| structured_swapped | 0.0% | 100.0% (13) | 100.0% (13) | 0.0% (13) | 84.6% (13) | 100.0% (13) | 100.0% (13) |

## Worst failures

- `JP-n1951880754` [line_messy] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": " 160‐0021 新宿区 \tまねき通り１丁目１一６,"}` -> mismatched predictions `{"house_number": "新宿区 0021 160‐0021", "street": "新宿区 0021 160‐0021", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n2262375007` [line_messy] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": " 101–0025 千代田区 環状2号線１丁目６一４"}` -> mismatched predictions `{"house_number": "千代田区 0025 101–0025", "street": "千代田区 0025 101–0025", "city": "", "postcode": ""}` (confidence 0.94)
- `PT-n2884148401` [line_nocomma] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "PT", "street1": "Travessa da Queimada 7 - 9 1200-285 Lisboa"}` -> mismatched predictions `{"house_number": "TRAVESSA DA QUEIMADA 7", "street": "TRAVESSA DA QUEIMADA 7", "city": "", "postcode": ""}` (confidence 0.94)
- `RU-n1722577439` [line_nocomma] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "RU", "street1": "119034 Москва Пречистенская набережная, 9"}` -> mismatched predictions `{"house_number": "119034 МОСКВА ПРЕЧИСТЕНСКАЯ НАБЕРЕЖНАЯ", "street": "119034 МОСКВА ПРЕЧИСТЕНСКАЯ НАБЕРЕЖНАЯ", "city": "9", "postcode": ""}` (confidence 0.985)
- `RU-n2542281163` [line_nocomma] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "RU", "street1": "109147 Москва Таганская улица, 2"}` -> mismatched predictions `{"house_number": "109147 МОСКВА ТАГАНСКАЯ УЛИЦА", "street": "109147 МОСКВА ТАГАНСКАЯ УЛИЦА", "city": "2", "postcode": ""}` (confidence 0.985)
- `TW-n1966685994` [line] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "TW", "street1": "105 台北市 復興北路231巷34"}` -> mismatched predictions `{"house_number": "台北市 105", "street": "台北市 105", "city": "", "postcode": ""}` (confidence 0.94)
- `TW-n1966685994` [line_country_text] failed ['city', 'house_number', 'postcode', 'street']: input `{"street1": "105 台北市 復興北路231巷34 Taiwan"}` -> mismatched predictions `{"house_number": "台北市 105", "street": "台北市 105", "city": "", "postcode": ""}` (confidence 0.94)
- `TW-n1966685994` [line_lower] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "TW", "street1": "105 台北市 復興北路231巷34"}` -> mismatched predictions `{"house_number": "台北市 105", "street": "台北市 105", "city": "", "postcode": ""}` (confidence 0.94)
- `TW-n1966685994` [line_messy] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "TW", "street1": " 105 台北市 復興北路231巷34 "}` -> mismatched predictions `{"house_number": "台北市 105", "street": "台北市 105", "city": "", "postcode": ""}` (confidence 0.94)
- `TW-n1966685994` [line_nocomma] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "TW", "street1": "105 台北市 復興北路231巷34"}` -> mismatched predictions `{"house_number": "台北市 105", "street": "台北市 105", "city": "", "postcode": ""}` (confidence 0.94)
- `TW-n1966685994` [line_upper] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "TW", "street1": "105 台北市 復興北路231巷34"}` -> mismatched predictions `{"house_number": "台北市 105", "street": "台北市 105", "city": "", "postcode": ""}` (confidence 0.94)
- `TW-n1978019287` [line] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "TW", "street1": "106 臺北市 光復南路280巷47"}` -> mismatched predictions `{"house_number": "臺北市 106", "street": "臺北市 106", "city": "", "postcode": ""}` (confidence 0.94)
- `TW-n1978019287` [line_country_text] failed ['city', 'house_number', 'postcode', 'street']: input `{"street1": "106 臺北市 光復南路280巷47 Taiwan"}` -> mismatched predictions `{"house_number": "臺北市 106", "street": "臺北市 106", "city": "", "postcode": ""}` (confidence 0.94)
- `TW-n1978019287` [line_lower] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "TW", "street1": "106 臺北市 光復南路280巷47"}` -> mismatched predictions `{"house_number": "臺北市 106", "street": "臺北市 106", "city": "", "postcode": ""}` (confidence 0.94)
- `TW-n1978019287` [line_messy] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "TW", "street1": " 106  臺北市 光復南路280巷47"}` -> mismatched predictions `{"house_number": "臺北市 106", "street": "臺北市 106", "city": "", "postcode": ""}` (confidence 0.94)

## Raw confidence score vs. observed all-fields correctness

n = 2417, observed exact-match rate = 64.2%, ECE = 0.310, Brier = 0.310. The raw score is a rule-based heuristic, not a probability.

| bin | n | mean score | observed exact |
|---|---|---|---|
| [0.0, 0.1) | 66 | 0.000 | 0.0% |
| [0.8, 0.9) | 22 | 0.881 | 40.9% |
| [0.9, 1.0) | 2329 | 0.980 | 66.2% |

## Confidence calibration on the OSM sample

Observed all-fields exact-match rate: 64.2%.

Held-out half (fit on a disjoint half of the records, split by record id):

| score | n | ECE | Brier |
|---|---|---|---|
| raw composite | 1231 | 0.289 | 0.289 |
| isotonic-calibrated | 1231 | 0.048 | 0.150 |

In-sample (optimistic for the calibrator): raw ECE 0.310 / Brier 0.310; calibrated ECE 0.005 / Brier 0.160.

## Reliability table (raw score, all rows)

| bin | n | mean score | observed exact | gap |
|---|---|---|---|---|
| [0.0, 0.1) | 66 | 0.000 | 0.0% | +0.000 |
| [0.8, 0.9) | 22 | 0.881 | 40.9% | -0.472 |
| [0.9, 1.0) | 2329 | 0.980 | 66.2% | -0.318 |

The raw score is a heuristic, not a probability; this table shows how far it is from one on this sample.
