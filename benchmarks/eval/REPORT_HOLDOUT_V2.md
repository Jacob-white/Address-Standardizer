# Independent accuracy evaluation

Corpus: 1506 OSM-derived records, 12872 input renderings (seed 20270115). Ground truth = OpenStreetMap `addr:*` tags; NOT human-reviewed. (c) OpenStreetMap contributors, ODbL 1.0.

Accuracy = correct / labelled; precision = correct / (correct + wrong); 95% Wilson interval on accuracy.

**All-fields exact match (all renderings): 92.2%** (11863/12872, 95% CI 91.7% - 92.6%)

## Overall by field

| field | n | accuracy | precision | 95% CI |
|---|---|---|---|---|
| house_number | 12872 | 98.8% | 99.1% | 98.6% - 99.0% |
| street | 12872 | 96.0% | 96.0% | 95.6% - 96.3% |
| city | 12872 | 96.5% | 97.4% | 96.2% - 96.8% |
| state | 1091 | 66.5% | 89.4% | 63.6% - 69.2% |
| postcode | 11366 | 98.4% | 99.9% | 98.1% - 98.6% |
| country | 12872 | 100.0% | 100.0% | 100.0% - 100.0% |

## By country and field (accuracy, n)

| country | exact | house_number | street | city | state | postcode | country |
|---|---|---|---|---|---|---|---|
| AR | 40.8% | 100.0% (282) | 100.0% (282) | 91.5% (282) | 13.5% (193) | 100.0% (252) | 100.0% (282) |
| AT | 100.0% | 100.0% (263) | 100.0% (263) | 100.0% (263) | - | 100.0% (233) | 100.0% (263) |
| AU | 91.0% | 99.7% (321) | 99.7% (321) | 91.3% (321) | 100.0% (294) | 100.0% (291) | 100.0% (321) |
| BE | 96.0% | 100.0% (250) | 96.0% (250) | 100.0% (250) | - | 100.0% (220) | 100.0% (250) |
| BR | 92.9% | 98.9% (268) | 94.0% (268) | 98.9% (268) | - | 100.0% (238) | 100.0% (268) |
| CA | 90.0% | 100.0% (309) | 96.1% (309) | 93.9% (309) | 87.4% (238) | 100.0% (279) | 100.0% (309) |
| CH | 100.0% | 100.0% (251) | 100.0% (251) | 100.0% (251) | - | 100.0% (221) | 100.0% (251) |
| CL | 85.8% | 100.0% (253) | 100.0% (253) | 96.8% (253) | 10.0% (40) | 100.0% (223) | 100.0% (253) |
| CO | 55.8% | 100.0% (265) | 64.9% (265) | 87.5% (265) | 9.4% (32) | 84.7% (235) | 100.0% (265) |
| CZ | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| DE | 100.0% | 100.0% (267) | 100.0% (267) | 100.0% (267) | - | 100.0% (237) | 100.0% (267) |
| DK | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| EC | 94.7% | 99.6% (244) | 98.8% (244) | 94.7% (244) | - | 96.3% (214) | 100.0% (244) |
| EG | 91.2% | 100.0% (240) | 91.2% (240) | 91.2% (240) | - | 99.0% (210) | 100.0% (240) |
| ES | 100.0% | 100.0% (258) | 100.0% (258) | 100.0% (258) | - | 100.0% (228) | 100.0% (258) |
| FI | 93.3% | 93.3% (240) | 93.3% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| FR | 99.6% | 100.0% (243) | 99.6% (243) | 100.0% (243) | - | 100.0% (213) | 100.0% (243) |
| GB | 100.0% | 100.0% (264) | 100.0% (264) | 100.0% (264) | - | 100.0% (234) | 100.0% (264) |
| GR | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| HU | 98.3% | 98.3% (240) | 98.3% (240) | 98.3% (240) | - | 100.0% (210) | 100.0% (240) |
| ID | 74.6% | 100.0% (240) | 77.9% (240) | 74.6% (240) | - | 97.6% (210) | 100.0% (240) |
| IE | 100.0% | 100.0% (263) | 100.0% (263) | 100.0% (263) | - | 100.0% (233) | 100.0% (263) |
| IL | 99.2% | 100.0% (240) | 99.2% (240) | 99.2% (240) | - | 99.0% (210) | 100.0% (240) |
| IN | 89.1% | 100.0% (267) | 96.3% (267) | 94.8% (267) | 4.8% (21) | 100.0% (237) | 100.0% (267) |
| IT | 89.6% | 100.0% (268) | 89.6% (268) | 100.0% (268) | - | 100.0% (238) | 100.0% (268) |
| JP | 64.6% | 74.2% (240) | 70.4% (240) | 88.3% (240) | - | 97.1% (210) | 100.0% (240) |
| KE | 77.6% | 93.7% (143) | 90.9% (143) | 78.3% (143) | - | 77.2% (127) | 100.0% (143) |
| KR | 96.7% | 96.7% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| MX | 79.6% | 100.0% (280) | 99.6% (280) | 93.9% (280) | 35.1% (77) | 97.2% (250) | 100.0% (280) |
| MY | 96.7% | 96.7% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| NG | 94.7% | 100.0% (263) | 98.1% (263) | 98.1% (263) | 18.2% (11) | 97.9% (233) | 100.0% (263) |
| NL | 94.1% | 100.0% (255) | 94.1% (255) | 100.0% (255) | - | 100.0% (225) | 100.0% (255) |
| NO | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| NZ | 100.0% | 100.0% (270) | 100.0% (270) | 100.0% (270) | - | 100.0% (240) | 100.0% (270) |
| PE | 82.5% | 100.0% (269) | 99.3% (269) | 91.8% (269) | 19.4% (31) | 90.8% (239) | 100.0% (269) |
| PH | 98.1% | 100.0% (268) | 98.1% (268) | 98.1% (268) | - | 97.9% (238) | 100.0% (268) |
| PL | 96.7% | 100.0% (241) | 96.7% (241) | 100.0% (241) | - | 100.0% (211) | 100.0% (241) |
| PT | 98.5% | 100.0% (265) | 98.5% (265) | 98.5% (265) | - | 98.3% (235) | 100.0% (265) |
| RO | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| RU | 93.3% | 94.8% (269) | 93.3% (269) | 94.4% (269) | - | 99.2% (239) | 100.0% (269) |
| SA | 80.0% | 93.3% (240) | 84.6% (240) | 85.8% (240) | - | 94.3% (210) | 100.0% (240) |
| SE | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| SG | 100.0% | 100.0% (264) | 100.0% (264) | 100.0% (264) | - | 100.0% (234) | 100.0% (264) |
| TH | 91.7% | 96.7% (240) | 91.7% (240) | 95.0% (240) | - | 96.7% (210) | 100.0% (240) |
| TR | 96.2% | 100.0% (240) | 96.2% (240) | 99.6% (240) | - | 99.5% (210) | 100.0% (240) |
| TW | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| UA | 99.4% | 100.0% (177) | 99.4% (177) | 99.4% (177) | - | 100.0% (157) | 100.0% (177) |
| US | 98.0% | 100.0% (298) | 98.0% (298) | 98.0% (298) | 100.0% (154) | 100.0% (268) | 100.0% (298) |
| UY | 100.0% | 100.0% (247) | 100.0% (247) | 100.0% (247) | - | 100.0% (217) | 100.0% (247) |
| VN | 87.1% | 100.0% (240) | 87.1% (240) | 87.5% (240) | - | 85.7% (210) | 100.0% (240) |
| ZA | 96.6% | 100.0% (267) | 99.3% (267) | 96.6% (267) | - | 99.6% (237) | 100.0% (267) |

## By input style and field (accuracy, n)

| style | exact | house_number | street | city | state | postcode | country |
|---|---|---|---|---|---|---|---|
| line | 93.8% | 98.8% (1506) | 97.3% (1506) | 97.9% (1506) | 63.7% (102) | 98.9% (1506) | 100.0% (1506) |
| line_abbrev | 87.3% | 99.5% (620) | 90.3% (620) | 98.4% (620) | 81.7% (71) | 98.7% (620) | 100.0% (620) |
| line_country_text | 93.9% | 98.9% (1506) | 97.4% (1506) | 98.0% (1506) | 63.7% (102) | 98.9% (1506) | 100.0% (1506) |
| line_lower | 93.8% | 98.8% (1506) | 97.3% (1506) | 97.9% (1506) | 63.7% (102) | 98.9% (1506) | 100.0% (1506) |
| line_messy | 93.8% | 98.8% (1506) | 97.3% (1506) | 97.9% (1506) | 63.7% (102) | 98.9% (1506) | 100.0% (1506) |
| line_no_postal | 94.2% | 98.5% (1506) | 97.6% (1506) | 98.5% (1506) | 63.7% (102) | - | 100.0% (1506) |
| line_nocomma | 85.3% | 98.6% (1506) | 88.0% (1506) | 89.2% (1506) | 63.7% (102) | 93.9% (1506) | 100.0% (1506) |
| line_swapped | 52.0% | 100.0% (102) | 87.3% (102) | 74.5% (102) | 52.0% (102) | 97.1% (102) | 100.0% (102) |
| line_upper | 93.8% | 98.8% (1506) | 97.3% (1506) | 97.9% (1506) | 63.7% (102) | 98.9% (1506) | 100.0% (1506) |
| structured | 97.8% | 99.0% (1506) | 98.1% (1506) | 100.0% (1506) | 99.0% (102) | 100.0% (1506) | 100.0% (1506) |
| structured_swapped | 30.4% | 100.0% (102) | 99.0% (102) | 30.4% (102) | 56.9% (102) | 100.0% (102) | 100.0% (102) |

## Worst failures

- `CO-w542648388` [line] failed ['city', 'postcode', 'state', 'street']: input `{"country": "CO", "street1": "Carrera 46 61-14, Medellín, 057"}` -> mismatched predictions `{"street": "CRA 46 61-14", "city": "MEDELLÍN 057", "state": "", "postcode": ""}` (confidence 0.985)
- `CO-w542648388` [line_country_text] failed ['city', 'postcode', 'state', 'street']: input `{"street1": "Carrera 46 61-14, Medellín, 057, Colombia"}` -> mismatched predictions `{"street": "CRA 46 61-14", "city": "MEDELLÍN 057", "state": "", "postcode": ""}` (confidence 0.985)
- `CO-w542648388` [line_lower] failed ['city', 'postcode', 'state', 'street']: input `{"country": "CO", "street1": "carrera 46 61-14, medellín, 057"}` -> mismatched predictions `{"street": "CRA 46 61-14", "city": "MEDELLÍN 057", "state": "", "postcode": ""}` (confidence 0.985)
- `CO-w542648388` [line_messy] failed ['city', 'postcode', 'state', 'street']: input `{"country": "CO", "street1": " Carrera 46  61‐14, Medellín, 057,"}` -> mismatched predictions `{"street": "CRA 46 61-14", "city": "MEDELLÍN 057", "state": "", "postcode": ""}` (confidence 0.985)
- `CO-w542648388` [line_nocomma] failed ['city', 'postcode', 'state', 'street']: input `{"country": "CO", "street1": "Carrera 46 61-14 Medellín 057"}` -> mismatched predictions `{"street": "CRA 46 61-14 MEDELLÍN 057", "city": "", "state": "", "postcode": ""}` (confidence 0.94)
- `CO-w542648388` [line_swapped] failed ['city', 'postcode', 'state', 'street']: input `{"country": "CO", "street1": "Carrera 46 61-14, ANT, 057"}` -> mismatched predictions `{"street": "CRA 46 61-14", "city": "ANT 057", "state": "", "postcode": ""}` (confidence 0.985)
- `CO-w542648388` [line_upper] failed ['city', 'postcode', 'state', 'street']: input `{"country": "CO", "street1": "CARRERA 46 61-14, MEDELLÍN, 057"}` -> mismatched predictions `{"street": "CRA 46 61-14", "city": "MEDELLÍN 057", "state": "", "postcode": ""}` (confidence 0.985)
- `CO-w542648399` [line_nocomma] failed ['city', 'postcode', 'state', 'street']: input `{"country": "CO", "street1": "Calle 53 40-65 Medellín 057"}` -> mismatched predictions `{"street": "CALLE 53 40-65 MEDELLÍN 057", "city": "", "state": "", "postcode": ""}` (confidence 0.94)
- `EC-n1778229007` [line_country_text] failed ['city', 'house_number', 'postcode', 'street']: input `{"street1": "Mariscal Lamar 6-44, 010101 Cuenca, Ecuador, Ecuador"}` -> mismatched predictions `{"house_number": "010101 CUENCA", "street": "010101 CUENCA", "city": "ECUADOR", "postcode": ""}` (confidence 0.985)
- `JP-n3446415095` [line] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "605-0084 Kyoto Kiyomotocho372"}` -> mismatched predictions `{"house_number": "605-0084 KYOTO KIYOMOTOCHO372", "street": "605-0084 KYOTO KIYOMOTOCHO372", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n3446415095` [line_country_text] failed ['city', 'house_number', 'postcode', 'street']: input `{"street1": "605-0084 Kyoto Kiyomotocho372 Japan"}` -> mismatched predictions `{"house_number": "605-0084 KYOTO KIYOMOTOCHO372 JAPAN", "street": "605-0084 KYOTO KIYOMOTOCHO372 JAPAN", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n3446415095` [line_lower] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "605-0084 kyoto kiyomotocho372"}` -> mismatched predictions `{"house_number": "605-0084 KYOTO KIYOMOTOCHO372", "street": "605-0084 KYOTO KIYOMOTOCHO372", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n3446415095` [line_messy] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "605‐0084 \tKyoto Kiyomotocho372,"}` -> mismatched predictions `{"house_number": "605-0084 KYOTO KIYOMOTOCHO372", "street": "605-0084 KYOTO KIYOMOTOCHO372", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n3446415095` [line_nocomma] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "605-0084 Kyoto Kiyomotocho372"}` -> mismatched predictions `{"house_number": "605-0084 KYOTO KIYOMOTOCHO372", "street": "605-0084 KYOTO KIYOMOTOCHO372", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n3446415095` [line_upper] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "605-0084 KYOTO KIYOMOTOCHO372"}` -> mismatched predictions `{"house_number": "605-0084 KYOTO KIYOMOTOCHO372", "street": "605-0084 KYOTO KIYOMOTOCHO372", "city": "", "postcode": ""}` (confidence 0.94)

## Raw confidence score vs. observed all-fields correctness

n = 12872, observed exact-match rate = 92.2%, ECE = 0.064, Brier = 0.076. The raw score is a rule-based heuristic, not a probability.

| bin | n | mean score | observed exact |
|---|---|---|---|
| [0.5, 0.6) | 16 | 0.560 | 100.0% |
| [0.7, 0.8) | 1 | 0.773 | 100.0% |
| [0.8, 0.9) | 28 | 0.880 | 100.0% |
| [0.9, 1.0) | 12827 | 0.985 | 92.1% |
