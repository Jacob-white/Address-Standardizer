# Independent accuracy evaluation

Corpus: 282 OSM-derived records, 2417 input renderings (seed 20261009). Ground truth = OpenStreetMap `addr:*` tags; NOT human-reviewed. (c) OpenStreetMap contributors, ODbL 1.0.

Accuracy = correct / labelled; precision = correct / (correct + wrong); 95% Wilson interval on accuracy.

**All-fields exact match (all renderings): 93.7%** (2265/2417, 95% CI 92.7% - 94.6%)

## Overall by field

| field | n | accuracy | precision | 95% CI |
|---|---|---|---|---|
| house_number | 2417 | 100.0% | 100.0% | 99.8% - 100.0% |
| street | 2417 | 94.4% | 94.4% | 93.4% - 95.3% |
| city | 2417 | 95.2% | 98.7% | 94.3% - 96.0% |
| state | 143 | 95.8% | 98.6% | 91.1% - 98.1% |
| postcode | 2135 | 97.0% | 100.0% | 96.2% - 97.7% |
| country | 2417 | 100.0% | 100.0% | 99.8% - 100.0% |

## By country and field (accuracy, n)

| country | exact | house_number | street | city | state | postcode | country |
|---|---|---|---|---|---|---|---|
| AT | 98.9% | 100.0% (93) | 98.9% (93) | 100.0% (93) | - | 100.0% (82) | 100.0% (93) |
| BE | 79.5% | 100.0% (88) | 79.5% (88) | 88.6% (88) | - | 87.2% (78) | 100.0% (88) |
| BR | 100.0% | 100.0% (99) | 100.0% (99) | 100.0% (99) | - | 100.0% (88) | 100.0% (99) |
| CA | 84.7% | 100.0% (98) | 86.7% (98) | 86.7% (98) | 72.7% (22) | 100.0% (87) | 100.0% (98) |
| CH | 100.0% | 100.0% (96) | 100.0% (96) | 100.0% (96) | - | 100.0% (85) | 100.0% (96) |
| DE | 100.0% | 100.0% (98) | 100.0% (98) | 100.0% (98) | - | 100.0% (87) | 100.0% (98) |
| DK | 100.0% | 100.0% (88) | 100.0% (88) | 100.0% (88) | - | 100.0% (77) | 100.0% (88) |
| ES | 100.0% | 100.0% (92) | 100.0% (92) | 100.0% (92) | - | 100.0% (81) | 100.0% (92) |
| FR | 100.0% | 100.0% (90) | 100.0% (90) | 100.0% (90) | - | 100.0% (79) | 100.0% (90) |
| GB | 88.8% | 100.0% (98) | 88.8% (98) | 88.8% (98) | - | 87.4% (87) | 100.0% (98) |
| GR | 87.5% | 100.0% (88) | 87.5% (88) | 87.5% (88) | - | 85.7% (77) | 100.0% (88) |
| IE | 88.5% | 100.0% (96) | 88.5% (96) | 100.0% (96) | - | 100.0% (85) | 100.0% (96) |
| IL | 87.5% | 100.0% (88) | 87.5% (88) | 87.5% (88) | - | 85.7% (77) | 100.0% (88) |
| IT | 88.9% | 100.0% (99) | 88.9% (99) | 100.0% (99) | - | 100.0% (88) | 100.0% (99) |
| JP | 100.0% | 100.0% (64) | 100.0% (64) | 100.0% (64) | - | 100.0% (56) | 100.0% (64) |
| KR | 100.0% | 100.0% (88) | 100.0% (88) | 100.0% (88) | - | 100.0% (77) | 100.0% (88) |
| NL | 97.8% | 100.0% (90) | 97.8% (90) | 100.0% (90) | - | 100.0% (79) | 100.0% (90) |
| NZ | 88.8% | 100.0% (98) | 88.8% (98) | 88.8% (98) | - | 87.4% (87) | 100.0% (98) |
| PL | 87.8% | 100.0% (90) | 87.8% (90) | 87.8% (90) | - | 100.0% (79) | 100.0% (90) |
| PT | 100.0% | 100.0% (97) | 100.0% (97) | 100.0% (97) | - | 100.0% (86) | 100.0% (97) |
| RU | 100.0% | 100.0% (96) | 100.0% (96) | 100.0% (96) | - | 100.0% (85) | 100.0% (96) |
| SE | 100.0% | 100.0% (88) | 100.0% (88) | 100.0% (88) | - | 100.0% (77) | 100.0% (88) |
| TH | 80.7% | 100.0% (88) | 81.8% (88) | 80.7% (88) | - | 87.0% (77) | 100.0% (88) |
| TW | 100.0% | 100.0% (88) | 100.0% (88) | 100.0% (88) | - | 100.0% (77) | 100.0% (88) |
| UA | 100.0% | 100.0% (98) | 100.0% (98) | 100.0% (98) | - | 100.0% (87) | 100.0% (98) |
| US | 81.8% | 100.0% (121) | 93.4% (121) | 82.6% (121) | 100.0% (121) | 100.0% (110) | 100.0% (121) |

## By input style and field (accuracy, n)

| style | exact | house_number | street | city | state | postcode | country |
|---|---|---|---|---|---|---|---|
| line | 99.6% | 100.0% (282) | 99.6% (282) | 99.6% (282) | 100.0% (13) | 100.0% (282) | 100.0% (282) |
| line_abbrev | 83.7% | 100.0% (135) | 83.7% (135) | 100.0% (135) | 100.0% (13) | 100.0% (135) | 100.0% (135) |
| line_country_text | 99.6% | 100.0% (282) | 99.6% (282) | 99.6% (282) | 100.0% (13) | 100.0% (282) | 100.0% (282) |
| line_lower | 99.6% | 100.0% (282) | 99.6% (282) | 99.6% (282) | 100.0% (13) | 100.0% (282) | 100.0% (282) |
| line_messy | 99.6% | 100.0% (282) | 99.6% (282) | 99.6% (282) | 100.0% (13) | 100.0% (282) | 100.0% (282) |
| line_no_postal | 99.6% | 100.0% (282) | 100.0% (282) | 99.6% (282) | 100.0% (13) | - | 100.0% (282) |
| line_nocomma | 65.2% | 100.0% (282) | 65.2% (282) | 69.1% (282) | 84.6% (13) | 77.3% (282) | 100.0% (282) |
| line_swapped | 0.0% | 100.0% (13) | 23.1% (13) | 23.1% (13) | 84.6% (13) | 100.0% (13) | 100.0% (13) |
| line_upper | 99.6% | 100.0% (282) | 99.6% (282) | 99.6% (282) | 100.0% (13) | 100.0% (282) | 100.0% (282) |
| structured | 100.0% | 100.0% (282) | 100.0% (282) | 100.0% (282) | 100.0% (13) | 100.0% (282) | 100.0% (282) |
| structured_swapped | 0.0% | 100.0% (13) | 100.0% (13) | 0.0% (13) | 84.6% (13) | 100.0% (13) | 100.0% (13) |

## Worst failures

- `BE-n11393794986` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "BE", "street1": "Rue Haute - Hoogstraat 64 1000 Bruxelles - Brussel"}` -> mismatched predictions `{"street": "RUE HAUTE - HOOGSTRAAT 64 1000 BRUXELLES - BRUSSEL", "city": "", "postcode": ""}` (confidence 0.94)
- `BE-n2327876130` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "BE", "street1": "Rue Auguste Hainaut - Auguste Hainautstraat 8 1090 Jette"}` -> mismatched predictions `{"street": "RUE AUGUSTE HAINAUT - AUGUSTE HAINAUTSTRAAT 8 1090 JETTE", "city": "", "postcode": ""}` (confidence 0.94)
- `CA-n267314310` [line_nocomma] failed ['city', 'state', 'street']: input `{"country": "CA", "street1": "20 Dundas Street West Toronto Ontario M5G 2C2"}` -> mismatched predictions `{"street": "20 DUNDAS ST W TORONTO ONTARIO", "city": "", "state": ""}` (confidence 0.94)
- `CA-n380027357` [line_nocomma] failed ['city', 'state', 'street']: input `{"country": "CA", "street1": "600 Sherbourne Street Toronto Ontario M4X 1W4"}` -> mismatched predictions `{"street": "600 SHERBOURNE ST TORONTO ONTARIO", "city": "", "state": ""}` (confidence 0.94)
- `GB-n259253467` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "GB", "street1": "11 Talbot Court London EC3V 0BP"}` -> mismatched predictions `{"street": "11 TALBOT CT LONDON EC3V 0BP", "city": "", "postcode": ""}` (confidence 0.94)
- `GB-n265662788` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "GB", "street1": "314-316 Vauxhall Bridge Road London SW1V 1AA"}` -> mismatched predictions `{"street": "314-316 VAUXHALL BRIDGE RD LONDON SW1V 1AA", "city": "", "postcode": ""}` (confidence 0.94)
- `GR-n1434326599` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "GR", "street1": "Μιχαήλ Βόδα 85 10440 Αθήνα"}` -> mismatched predictions `{"street": "ΜΙΧΑΉΛ ΒΌΔΑ 85 10440 ΑΘΉΝΑ", "city": "", "postcode": ""}` (confidence 0.94)
- `GR-n1579872651` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "GR", "street1": "Κρέσνας 70 11363 Αθήνα"}` -> mismatched predictions `{"street": "ΚΡΈΣΝΑΣ 70 11363 ΑΘΉΝΑ", "city": "", "postcode": ""}` (confidence 0.94)
- `IL-n12908886701` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "IL", "street1": "האומנים 12 תל אביב 6789731"}` -> mismatched predictions `{"street": "האומנים 12 תל אביב 6789731", "city": "", "postcode": ""}` (confidence 0.94)
- `IL-n3887425957` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "IL", "street1": "Bulevardul Shaul HaMelech 8 Tel Aviv 64733"}` -> mismatched predictions `{"street": "BULEVARDUL SHAUL HAMELECH 8 TEL AVIV 64733", "city": "", "postcode": ""}` (confidence 0.94)
- `NZ-n1668158092` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "NZ", "street1": "43 Elliot Street Auckland 1010"}` -> mismatched predictions `{"street": "43 ELLIOT ST AUCKLAND 1010", "city": "", "postcode": ""}` (confidence 0.94)
- `NZ-n1668246153` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "NZ", "street1": "20 Victoria Street West Auckland 1010"}` -> mismatched predictions `{"street": "20 VICTORIA ST WEST AUCKLAND 1010", "city": "", "postcode": ""}` (confidence 0.94)
- `TH-n10723897686` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "TH", "street1": "10/1 Rachadamnoen Road Soi 5 Chiang Mai 50200"}` -> mismatched predictions `{"street": "10/1 RACHADAMNOEN RD SOI 5 CHIANG MAI 50200", "city": "", "postcode": ""}` (confidence 0.94)
- `TH-n13202529004` [line_nocomma] failed ['city', 'postcode', 'street']: input `{"country": "TH", "street1": "16/1 Nimmanhaemin Soi 6 Chiang Mai 50200"}` -> mismatched predictions `{"street": "16/1 NIMMANHAEMIN SOI 6 CHIANG MAI 50200", "city": "", "postcode": ""}` (confidence 0.94)
- `CA-n267314310` [line_swapped] failed ['state', 'street']: input `{"country": "CA", "street1": "20 Dundas Street West, Ontario, Toronto M5G 2C2"}` -> mismatched predictions `{"street": "20 DUNDAS ST W ONTARIO", "state": ""}` (confidence 0.985)

## Raw confidence score vs. observed all-fields correctness

n = 2417, observed exact-match rate = 93.7%, ECE = 0.045, Brier = 0.057. The raw score is a rule-based heuristic, not a probability.

| bin | n | mean score | observed exact |
|---|---|---|---|
| [0.8, 0.9) | 22 | 0.881 | 50.0% |
| [0.9, 1.0) | 2395 | 0.984 | 94.1% |
