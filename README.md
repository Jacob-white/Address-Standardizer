# Address Standardizer

[![CI](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/Jacob-white/Address-Standardizer)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Standard](https://img.shields.io/badge/USPS-Publication%2028-orange.svg)](https://pe.usps.com/text/pub28/welcome.htm)

A standalone, high-performance address standardization and entity resolution engine. Built to parse, clean, normalize, deduplicate, and geocode physical addresses across US and international jurisdictions without vendor lock-in or recurring API costs.

---

## Highlights & Features

- **USPS Publication 28 Compliance:** Normalizes street suffixes (`Avenue` &rarr; `AVE`, `Street` &rarr; `ST`, `Boulevard` &rarr; `BLVD`), directional indicators (`North` &rarr; `N`, `Southwest` &rarr; `SW`), secondary units (`Suite` &rarr; `STE`, `Floor` &rarr; `FL`, `Apartment` &rarr; `APT`), and standardizes PO Boxes.
- **Hybrid Parsing Engine:** Powered by Conditional Random Fields (CRF) tokenization via `usaddress` with a pure-Python, zero-dependency rule-based fallback matrix for maximum resilience.
- **Numbered Street & Ordinal Normalization:** Automatically converts written words and raw cardinals into standard ordinals (`Fifth Avenue` &rarr; `5TH AVE`, `100 First St` &rarr; `100 1ST ST`, `200 West 42nd St` &rarr; `200 W 42ND ST`), while preserving highway route markers (`Route 66`).
- **Two-Tier Matching Keys:** Generates deterministic clustering hashes at two granularities:
  - `normalized_address_key`: Suite/unit level matching (`{STREET1}|{STREET2}|{CITY}|{STATE}|{ZIP5}|{COUNTRY}`).
  - `building_key`: Physical structure level matching (`{STREET1}||{CITY}|{STATE}|{ZIP5}|{COUNTRY}`) to link co-located entities, parent companies, or multiple tenants in the same building.
- **Typo-Tolerant Phonetic Blocking:** Computes pure-Python American Soundex keys (`555 Montgomery St` &rarr; `555|M532|94111` and `555 Montgomeri St` &rarr; `555|M532|94111`) for fuzzy deduplication and entity resolution.
- **ZIP3 State Auto-Healing:** Recovers missing or corrupt state codes using USPS 3-digit ZIP routing tables (`10005` with missing or erroneous state heals automatically to `NY`).
- **Registered Agent & Formation Hub Detection:** Flags commercial mailbox and corporate shell addresses (e.g. 1209 North Orange St, CSC Little Falls, NRAI Greentree, Ugland House in Cayman Islands).
- **Batch Geocoding with Fallback Centroids:** Integrates with the public US Census Bureau Batch Geocoder (up to 10,000 records per HTTP request) and falls back to precomputed metro ZIP3 / state centroids so coordinates are never empty for valid locations.
- **Full CLI & Python API:** Use as an importable library or as a command-line tool.

---

## Installation

### Base Package (Zero-Dependency Rule-Based & Geocoding)
```bash
pip install .
```

### Full ML Support (Recommended)
Includes Conditional Random Fields (`usaddress` / `python-crfsuite`):
```bash
pip install ".[ml]"
```

### Development
```bash
pip install -e ".[dev]"
```

---

## Quickstart (Python API)

### 1. Basic Address Standardization
```python
from address_standardizer import standardize_address

# Pass as a single full string:
std = standardize_address("100 Wall Street, Suite 400, New York, NY 10005")
print(std.street1)                 # "100 WALL ST"
print(std.street2)                 # "STE 400"
print(std.city)                    # "NEW YORK"
print(std.state)                   # "NY"
print(std.postal_code)             # "10005"
print(std.normalized_address_key)  # "100 WALL ST|STE 400|NEW YORK|NY|10005|USA"
print(std.building_key)            # "100 WALL ST||NEW YORK|NY|10005|USA"
print(std.phonetic_key)            # "100|W400|10005"

# Or pass structured components:
std2 = standardize_address(
    street1="350 Fifth Avenue",
    street2="Floor 59",
    city="New York",
    state="New York",
    postal_code="10118-0110",
    country="United States",
)
print(std2.street1)                # "350 5TH AVE"
print(std2.street2)                # "FL 59"
print(std2.postal_code)            # "10118-0110"
print(std2.country)                # "USA"
```

### 2. Entity Resolution & Building-Level Clustering
```python
from address_standardizer import generate_normalized_address_key, generate_building_key

suite_a = "100 Main Street, Suite 500, Denver, CO 80202"
suite_b = "100 Main St., Floor 10, Denver, CO 80202"

# Distinct suite keys:
print(generate_normalized_address_key(suite_a))
# -> "100 MAIN ST|STE 500|DENVER|CO|80202|USA"
print(generate_normalized_address_key(suite_b))
# -> "100 MAIN ST|FL 10|DENVER|CO|80202|USA"

# Identical building keys:
print(generate_building_key(suite_a))
# -> "100 MAIN ST||DENVER|CO|80202|USA"
print(generate_building_key(suite_b))
# -> "100 MAIN ST||DENVER|CO|80202|USA"
```

### 3. Typo-Tolerant Phonetic Keys
```python
from address_standardizer import generate_phonetic_address_key

k1 = generate_phonetic_address_key("555 Montgomery Street", postal_or_zip="94111")
k2 = generate_phonetic_address_key("555 Montgomeri St", postal_or_zip="94111")

assert k1 == k2 == "555|M532|94111"
```

### 4. Registered Agent Hub Detection
```python
from address_standardizer import is_registered_agent_hub_address

# Delaware Corporation Trust Center
assert is_registered_agent_hub_address(
    street1="1209 North Orange Street",
    city="Wilmington",
    state="DE",
    postal_code="19801"
) is True

# Ugland House, Cayman Islands
assert is_registered_agent_hub_address(
    street1="PO Box 309, Ugland House",
    city="Grand Cayman",
    country="CYM"
) is True
```

### 5. High-Throughput Census Batch Geocoding
```python
from address_standardizer import CensusGeocoder, get_fallback_centroid

geocoder = CensusGeocoder(timeout_seconds=45)

records = [
    ("rec_1", "100 Wall Street", "New York", "NY", "10005"),
    ("rec_2", "1 Infinite Loop", "Cupertino", "CA", "95014"),
]

# Geocodes in batches up to 10,000 records via US Census Bureau
results = geocoder.geocode_batch(records, fallback_to_centroids=True)

print(results["rec_1"])
# {
#   'latitude': 40.7061,
#   'longitude': -74.0060,
#   'census_tract': '000700',
#   'precision': 'rooftop'
# }
```

---

## Command Line Interface (CLI)

The package installs the `address-standardizer` CLI executable.

### Single Address Parsing
```bash
# Shorthand:
address-standardizer "100 Wall Street, Suite 400, New York, NY 10005"

# With explicit parse subcommand and geocoding:
address-standardizer parse "350 5th Ave, New York, NY 10118" --geocode
```

Output:
```json
{
  "street1": "350 5TH AVE",
  "street2": "",
  "city": "NEW YORK",
  "state": "NY",
  "postal_code": "10118",
  "country": "USA",
  "normalized_address_key": "350 5TH AVE||NEW YORK|NY|10118|USA",
  "building_key": "350 5TH AVE||NEW YORK|NY|10118|USA",
  "phonetic_key": "350|T000|10118",
  "address_status": "standardized",
  "raw_street_address": "350 5th Ave, New York, NY 10118",
  "is_us": true,
  "is_private_residence": false,
  "is_registered_agent_hub": false,
  "latitude": 40.7484,
  "longitude": -73.9857,
  "geocode_precision": "rooftop"
}
```

### Batch CSV Standardization
Standardize an entire CSV file with multi-jurisdiction parsing and optional Census batch geocoding:

```bash
address-standardizer batch input_addresses.csv standardized_output.csv \
  --street-col street1 \
  --city-col city \
  --state-col state \
  --zip-col postal_code \
  --country-col country \
  --geocode
```

Appends standardized columns:
- `std_street1`, `std_street2`, `std_city`, `std_state`, `std_postal_code`, `std_country`
- `normalized_address_key`, `building_key`, `phonetic_key`
- `is_registered_agent_hub`, `is_private_residence`, `address_status`
- `latitude`, `longitude`, `geocode_precision` (if `--geocode` enabled)

---

## Data Model (`StandardizedAddress`)

```python
@dataclass
class StandardizedAddress:
    street1: str
    street2: str
    city: str
    state: str
    postal_code: str
    country: str
    normalized_address_key: Optional[str]
    address_status: str              # 'standardized' | 'parse_failed'
    raw_street_address: str
    is_us: bool
    is_private_residence: bool = False
    building_key: Optional[str] = None
    phonetic_key: Optional[str] = None
    is_registered_agent_hub: bool = False
```

---

## Running Tests

Run the test suite with `pytest`:

```bash
pytest -v
```

Run test suite with code coverage:

```bash
pytest --cov=address_standardizer --cov-report=term-missing
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
