# Independent accuracy evaluation

Corpus: 1182 OSM-derived records, 10106 input renderings (seed 20270302). Ground truth = OpenStreetMap `addr:*` tags; NOT human-reviewed. (c) OpenStreetMap contributors, ODbL 1.0.

Accuracy = correct / labelled; precision = correct / (correct + wrong); 95% Wilson interval on accuracy.

**All-fields exact match (all renderings): 94.5%** (9547/10106, 95% CI 94.0% - 94.9%)

## Overall by field

| field | n | accuracy | precision | 95% CI |
|---|---|---|---|---|
| house_number | 10106 | 99.6% | 99.9% | 99.4% - 99.7% |
| street | 10106 | 97.9% | 97.9% | 97.6% - 98.2% |
| city | 10106 | 96.9% | 97.5% | 96.5% - 97.2% |
| state | 984 | 78.4% | 93.1% | 75.7% - 80.8% |
| postcode | 8924 | 98.4% | 100.0% | 98.1% - 98.6% |
| country | 10106 | 100.0% | 100.0% | 100.0% - 100.0% |

## By country and field (accuracy, n)

| country | exact | house_number | street | city | state | postcode | country |
|---|---|---|---|---|---|---|---|
| AR | 99.6% | 100.0% (241) | 99.6% (241) | 99.6% (241) | - | 99.5% (211) | 100.0% (241) |
| AT | 100.0% | 100.0% (260) | 100.0% (260) | 100.0% (260) | - | 100.0% (230) | 100.0% (260) |
| AU | 100.0% | 100.0% (326) | 100.0% (326) | 100.0% (326) | 100.0% (326) | 100.0% (296) | 100.0% (326) |
| BE | 99.6% | 100.0% (246) | 99.6% (246) | 100.0% (246) | - | 100.0% (216) | 100.0% (246) |
| BR | 87.9% | 97.4% (265) | 90.6% (265) | 99.6% (265) | - | 99.6% (235) | 100.0% (265) |
| CA | 95.7% | 96.7% (302) | 99.7% (302) | 99.0% (302) | 100.0% (214) | 100.0% (272) | 100.0% (302) |
| CH | 96.8% | 100.0% (249) | 96.8% (249) | 96.8% (249) | - | 96.3% (219) | 100.0% (249) |
| CL | 100.0% | 100.0% (8) | 100.0% (8) | 100.0% (8) | - | 100.0% (7) | 100.0% (8) |
| CO | 96.1% | 96.5% (258) | 96.1% (258) | 99.6% (258) | - | 100.0% (228) | 100.0% (258) |
| CZ | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| DE | 100.0% | 100.0% (260) | 100.0% (260) | 100.0% (260) | - | 100.0% (230) | 100.0% (260) |
| DK | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| EC | 80.5% | 99.6% (236) | 97.5% (236) | 80.9% (236) | - | 77.9% (208) | 100.0% (236) |
| EG | 99.2% | 100.0% (128) | 99.2% (128) | 99.2% (128) | - | 100.0% (112) | 100.0% (128) |
| ES | 100.0% | 100.0% (268) | 100.0% (268) | 100.0% (268) | - | 100.0% (238) | 100.0% (268) |
| FI | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| FR | 100.0% | 100.0% (243) | 100.0% (243) | 100.0% (243) | - | 100.0% (213) | 100.0% (243) |
| GB | 100.0% | 100.0% (255) | 100.0% (255) | 100.0% (255) | - | 100.0% (225) | 100.0% (255) |
| HU | 99.2% | 99.2% (240) | 99.2% (240) | 99.2% (240) | - | 100.0% (210) | 100.0% (240) |
| ID | 67.9% | 100.0% (240) | 74.2% (240) | 67.9% (240) | - | 97.1% (210) | 100.0% (240) |
| IL | 100.0% | 100.0% (56) | 100.0% (56) | 100.0% (56) | - | 100.0% (49) | 100.0% (56) |
| IN | 92.7% | 100.0% (193) | 97.9% (193) | 96.9% (193) | 0.0% (10) | 100.0% (171) | 100.0% (193) |
| IT | 100.0% | 100.0% (268) | 100.0% (268) | 100.0% (268) | - | 100.0% (238) | 100.0% (268) |
| JP | 28.1% | 81.2% (32) | 50.0% (32) | 56.2% (32) | - | 78.6% (28) | 100.0% (32) |
| KE | 100.0% | 100.0% (18) | 100.0% (18) | 100.0% (18) | - | 100.0% (16) | 100.0% (18) |
| KR | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| MX | 70.6% | 100.0% (214) | 94.4% (214) | 89.7% (214) | 62.7% (142) | 100.0% (193) | 100.0% (214) |
| MY | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| NG | 100.0% | 100.0% (9) | 100.0% (9) | 100.0% (9) | - | 100.0% (8) | 100.0% (9) |
| NL | 100.0% | 100.0% (242) | 100.0% (242) | 100.0% (242) | - | 100.0% (212) | 100.0% (242) |
| NO | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| NZ | 100.0% | 100.0% (270) | 100.0% (270) | 100.0% (270) | - | 100.0% (240) | 100.0% (270) |
| PE | 30.9% | 100.0% (282) | 95.4% (282) | 72.3% (282) | 12.8% (172) | 82.5% (252) | 100.0% (282) |
| PH | 90.7% | 100.0% (161) | 90.7% (161) | 90.7% (161) | - | 89.5% (143) | 100.0% (161) |
| PL | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| PT | 100.0% | 100.0% (268) | 100.0% (268) | 100.0% (268) | - | 100.0% (238) | 100.0% (268) |
| RO | 100.0% | 100.0% (240) | 100.0% (240) | 100.0% (240) | - | 100.0% (210) | 100.0% (240) |
| RU | 99.3% | 100.0% (270) | 99.3% (270) | 100.0% (270) | - | 100.0% (240) | 100.0% (270) |
| SA | 93.8% | 100.0% (32) | 93.8% (32) | 93.8% (32) | - | 92.9% (28) | 100.0% (32) |
| SE | 100.0% | 100.0% (56) | 100.0% (56) | 100.0% (56) | - | 100.0% (49) | 100.0% (56) |
| SG | 93.9% | 100.0% (264) | 94.3% (264) | 97.0% (264) | - | 97.0% (234) | 100.0% (264) |
| TH | 96.9% | 100.0% (32) | 96.9% (32) | 96.9% (32) | - | 96.4% (28) | 100.0% (32) |
| TR | 99.2% | 100.0% (240) | 99.2% (240) | 99.2% (240) | - | 99.0% (210) | 100.0% (240) |
| TW | 90.8% | 96.7% (240) | 96.7% (240) | 94.2% (240) | - | 100.0% (210) | 100.0% (240) |
| US | 99.7% | 100.0% (287) | 99.7% (287) | 99.7% (287) | 100.0% (120) | 100.0% (257) | 100.0% (287) |
| UY | 100.0% | 100.0% (241) | 100.0% (241) | 100.0% (241) | - | 100.0% (211) | 100.0% (241) |
| VN | 94.4% | 100.0% (216) | 97.2% (216) | 94.4% (216) | - | 97.9% (189) | 100.0% (216) |
| ZA | 100.0% | 100.0% (270) | 100.0% (270) | 100.0% (270) | - | 100.0% (240) | 100.0% (270) |

## By input style and field (accuracy, n)

| style | exact | house_number | street | city | state | postcode | country |
|---|---|---|---|---|---|---|---|
| line | 94.6% | 99.6% (1182) | 98.3% (1182) | 97.3% (1182) | 76.1% (92) | 98.5% (1182) | 100.0% (1182) |
| line_abbrev | 96.6% | 99.8% (466) | 98.7% (466) | 98.9% (466) | 92.2% (64) | 98.9% (466) | 100.0% (466) |
| line_country_text | 94.6% | 99.6% (1182) | 98.3% (1182) | 97.3% (1182) | 76.1% (92) | 98.5% (1182) | 100.0% (1182) |
| line_lower | 94.6% | 99.6% (1182) | 98.3% (1182) | 97.3% (1182) | 76.1% (92) | 98.5% (1182) | 100.0% (1182) |
| line_messy | 94.6% | 99.6% (1182) | 98.3% (1182) | 97.3% (1182) | 76.1% (92) | 98.5% (1182) | 100.0% (1182) |
| line_no_postal | 95.8% | 99.5% (1182) | 99.0% (1182) | 98.5% (1182) | 76.1% (92) | - | 100.0% (1182) |
| line_nocomma | 91.4% | 99.5% (1182) | 92.9% (1182) | 93.2% (1182) | 76.1% (92) | 96.1% (1182) | 100.0% (1182) |
| line_swapped | 65.2% | 98.9% (92) | 98.9% (92) | 71.7% (92) | 68.5% (92) | 100.0% (92) | 100.0% (92) |
| line_upper | 94.6% | 99.6% (1182) | 98.3% (1182) | 97.3% (1182) | 76.1% (92) | 98.5% (1182) | 100.0% (1182) |
| structured | 98.8% | 99.7% (1182) | 99.2% (1182) | 99.9% (1182) | 98.9% (92) | 99.8% (1182) | 100.0% (1182) |
| structured_swapped | 72.8% | 98.9% (92) | 98.9% (92) | 73.9% (92) | 73.9% (92) | 100.0% (92) | 100.0% (92) |

## Worst failures

- `JP-n3476266893` [line] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "221-0005 Yokohama Matsumi-cho Kanagawa-like2-387-21"}` -> mismatched predictions `{"house_number": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21", "street": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n3476266893` [line_country_text] failed ['city', 'house_number', 'postcode', 'street']: input `{"street1": "221-0005 Yokohama Matsumi-cho Kanagawa-like2-387-21 Japan"}` -> mismatched predictions `{"house_number": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21 JAPAN", "street": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21 JAPAN", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n3476266893` [line_lower] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "221-0005 yokohama matsumi-cho kanagawa-like2-387-21"}` -> mismatched predictions `{"house_number": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21", "street": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n3476266893` [line_messy] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": " 221‐0005 Yokohama Matsumi‐cho  Kanagawa‐like2‐387‐21"}` -> mismatched predictions `{"house_number": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21", "street": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n3476266893` [line_nocomma] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "221-0005 Yokohama Matsumi-cho Kanagawa-like2-387-21"}` -> mismatched predictions `{"house_number": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21", "street": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21", "city": "", "postcode": ""}` (confidence 0.94)
- `JP-n3476266893` [line_upper] failed ['city', 'house_number', 'postcode', 'street']: input `{"country": "JP", "street1": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21"}` -> mismatched predictions `{"house_number": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21", "street": "221-0005 YOKOHAMA MATSUMI-CHO KANAGAWA-LIKE2-387-21", "city": "", "postcode": ""}` (confidence 0.94)
- `PE-n7873594127` [line_nocomma] failed ['city', 'postcode', 'state', 'street']: input `{"country": "PE", "street1": "Pasaje Pedro Canepa 183 La Victoria 15018"}` -> mismatched predictions `{"street": "PASAJE PEDRO CANEPA 183 LA VICTORIA 15018", "city": "", "state": "", "postcode": ""}` (confidence 0.94)
- `AR-n3812002446` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "AR", "street1": "Libertad Yapeyú 5539 Las Heras"}` -> mismatched predictions `{"street": "LIBERTAD YAPEYÚ 5539 LAS HERAS", "city": "", "postcode": ""}` (confidence 0.94)
- `BR-w1392469792` [line_nocomma] failed ['city', 'house_number', 'postcode']: input `{"country": "BR", "street1": "Rodovia Anel Rodoviário Celso Mello Azevedo, 20901 Belo Horizonte 31255-985"}` -> mismatched predictions `{"house_number": "RODOVIA ANEL RODOVIÁRIO CELSO MELLO AZEVEDO", "city": "BELO HORIZONTE 31255-985", "postcode": "20901"}` (confidence 0.985)
- `CH-n2829229177` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "CH", "street1": "Im Baselgarten 13 79576 Weil am Rhein"}` -> mismatched predictions `{"street": "IM BASELGARTEN 13 79576 WEIL AM RHEIN", "city": "", "postcode": ""}` (confidence 0.94)
- `CH-n467088930` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "CH", "street1": "Winzerweg 1 79576 Weil am Rhein"}` -> mismatched predictions `{"street": "WINZERWEG 1 79576 WEIL AM RHEIN", "city": "", "postcode": ""}` (confidence 0.94)
- `EC-n3945480757` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "EC", "street1": "Machala N53-88 17-01-04 Quito"}` -> mismatched predictions `{"street": "MACHALA N53-88 17-01-04 QUITO", "city": "", "postcode": ""}` (confidence 0.94)
- `EC-n3987039140` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "EC", "street1": "Calle G E11-40 EC170124 Quito"}` -> mismatched predictions `{"street": "CALLE G E11-40 EC170124 QUITO", "city": "", "postcode": ""}` (confidence 0.94)
- `HU-w593435633` [line_no_postal] failed ['city', 'house_number', 'street']: input `{"country": "HU", "street1": "Szeged, Hídverő utca 126/B"}` -> mismatched predictions `{"house_number": "SZEGED", "street": "SZEGED", "city": "HÍDVERŐ UTCA 126/B"}` (confidence 0.985)
- `HU-w593435636` [line_no_postal] failed ['city', 'house_number', 'street']: input `{"country": "HU", "street1": "Szeged, Hídverő utca 126/A"}` -> mismatched predictions `{"house_number": "SZEGED", "street": "SZEGED", "city": "HÍDVERŐ UTCA 126/A"}` (confidence 0.985)

## Raw confidence score vs. observed all-fields correctness

n = 10106, observed exact-match rate = 94.5%, ECE = 0.041, Brier = 0.054. The raw score is a rule-based heuristic, not a probability.

| bin | n | mean score | observed exact |
|---|---|---|---|
| [0.5, 0.6) | 19 | 0.560 | 100.0% |
| [0.8, 0.9) | 22 | 0.881 | 100.0% |
| [0.9, 1.0) | 10065 | 0.985 | 94.4% |
